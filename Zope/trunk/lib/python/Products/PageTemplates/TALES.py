##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""TALES

An implementation of a generic TALES engine
"""

__version__='$Revision: 1.25 $'[11:-2]

import re, sys, ZTUtils
from MultiMapping import MultiMapping

StringType = type('')

NAME_RE = r"[a-zA-Z][a-zA-Z0-9_]*"
_parse_expr = re.compile(r"(%s):" % NAME_RE).match
_valid_name = re.compile('%s$' % NAME_RE).match

class TALESError(Exception):
    __allow_access_to_unprotected_subobjects__ = 1
    def __init__(self, expression, info=(None, None, None),
                 position=(None, None)):
        self.type, self.value, self.traceback = info
        self.expression = expression
        self.setPosition(position)
    def setPosition(self, position):
        self.lineno = position[0]
        self.offset = position[1]
    def takeTraceback(self):
        t = self.traceback
        self.traceback = None
        return t
    def __str__(self):
        if self.type is None:
            s = self.expression
        else:
            s = '%s on %s in %s' % (self.type, self.value,
                                    `self.expression`)
        if self.lineno is not None:
            s = "%s, at line %d" % (s, self.lineno)
        if self.offset is not None:
            s = "%s, column %d" % (s, self.offset + 1)
        return s
    def __nonzero__(self):
        return 0

class Undefined(TALESError):
    '''Exception raised on traversal of an undefined path'''
    def __str__(self):
        if self.type is None:
            s = self.expression
        else:
            s = '%s not found in %s' % (self.value,
                                        `self.expression`)
        if self.lineno is not None:
            s = "%s, at line %d" % (s, self.lineno)
        if self.offset is not None:
            s = "%s, column %d" % (s, self.offset + 1)
        return s

class RegistrationError(Exception):
    '''TALES Type Registration Error'''

class CompilerError(Exception):
    '''TALES Compiler Error'''

class Default:
    '''Retain Default'''
    def __nonzero__(self):
        return 0
Default = Default()

_marker = []

class SafeMapping(MultiMapping):
    '''Mapping with security declarations and limited method exposure.

    Since it subclasses MultiMapping, this class can be used to wrap
    one or more mapping objects.  Restricted Python code will not be
    able to mutate the SafeMapping or the wrapped mappings, but will be
    able to read any value.
    '''
    __allow_access_to_unprotected_subobjects__ = 1
    push = pop = None

    _push = MultiMapping.push
    _pop = MultiMapping.pop

    def has_get(self, key, _marker=[]):
        v = self.get(key, _marker)
        return v is not _marker, v

class Iterator(ZTUtils.Iterator):
    def __init__(self, name, seq, context):
        ZTUtils.Iterator.__init__(self, seq)
        self.name = name
        self._context = context

    def next(self):
        try:
            if ZTUtils.Iterator.next(self):
                self._context.setLocal(self.name, self.item)
                return 1
        except TALESError:
            raise
        except:
            raise TALESError, ('repeat/%s' % self.name,
                               sys.exc_info()), sys.exc_info()[2]
        return 0


class Engine:
    '''Expression Engine

    An instance of this class keeps a mutable collection of expression
    type handlers.  It can compile expression strings by delegating to
    these handlers.  It can provide an expression Context, which is
    capable of holding state and evaluating compiled expressions.
    '''
    Iterator = Iterator

    def __init__(self, Iterator=None):
        self.types = {}
        if Iterator is not None:
            self.Iterator = Iterator

    def registerType(self, name, handler):
        if not _valid_name(name):
            raise RegistrationError, 'Invalid Expression type "%s".' % name
        types = self.types
        if types.has_key(name):
            raise RegistrationError, (
                'Multiple registrations for Expression type "%s".' %
                name)
        types[name] = handler

    def getTypes(self):
        return self.types

    def compile(self, expression):
        m = _parse_expr(expression)
        if m:
            type = m.group(1)
            expr = expression[m.end():]
        else:
            type = "standard"
            expr = expression
        try:
            handler = self.types[type]
        except KeyError:
            raise CompilerError, (
                'Unrecognized expression type "%s".' % type)
        return handler(type, expr, self)
    
    def getContext(self, contexts=None, **kwcontexts):
        if contexts is not None:
            if kwcontexts:
                kwcontexts.update(contexts)
            else:
                kwcontexts = contexts
        return Context(self, kwcontexts)

    def getCompilerError(self):
        return CompilerError

class Context:
    '''Expression Context

    An instance of this class holds context information that it can
    use to evaluate compiled expressions.
    '''

    _context_class = SafeMapping
    _nocatch = TALESError
    position = (None, None)

    def __init__(self, engine, contexts):
        self._engine = engine
        if hasattr(engine, '_nocatch'):
            self._nocatch = engine._nocatch
        self.contexts = contexts
        contexts['nothing'] = None
        contexts['default'] = Default

        self.repeat_vars = rv = {}
        # Wrap this, as it is visible to restricted code
        contexts['repeat'] = rep =  self._context_class(rv)
        contexts['loop'] = rep # alias

        self.global_vars = gv = contexts.copy()
        self.local_vars = lv = {}
        self.vars = self._context_class(gv, lv)

        # Keep track of what needs to be popped as each scope ends.
        self._scope_stack = []

    def beginScope(self):
        self._scope_stack.append([self.local_vars.copy()])

    def endScope(self):
        scope = self._scope_stack.pop()
        self.local_vars = lv = scope[0]
        v = self.vars
        v._pop()
        v._push(lv)
        # Pop repeat variables, if any
        i = len(scope) - 1
        while i:
            name, value = scope[i]
            if value is None:
                del self.repeat_vars[name]
            else:
                self.repeat_vars[name] = value
            i = i - 1

    def setLocal(self, name, value):
        self.local_vars[name] = value

    def setGlobal(self, name, value):
        self.global_vars[name] = value

    def setRepeat(self, name, expr):
        expr = self.evaluate(expr)
        if not expr:
            return self._engine.Iterator(name, (), self)
        it = self._engine.Iterator(name, expr, self)
        old_value = self.repeat_vars.get(name)
        self._scope_stack[-1].append((name, old_value))
        self.repeat_vars[name] = it
        return it

    def evaluate(self, expression,
                 isinstance=isinstance, StringType=StringType):
        if isinstance(expression, StringType):
            expression = self._engine.compile(expression)
        try:
            v = expression(self)
            if isinstance(v, Exception):
                if isinstance(v, TALESError):
                    raise v, None, v.takeTraceback()
                raise v
        except TALESError, err:
            err.setPosition(self.position)
            raise err, None, sys.exc_info()[2]
        except self._nocatch:
            raise
        except:
            raise TALESError, (`expression`, sys.exc_info(),
                               self.position), sys.exc_info()[2]
        else:
            return v

    evaluateValue = evaluate

    def evaluateBoolean(self, expr):
        return not not self.evaluate(expr)

    def evaluateText(self, expr, None=None):
        text = self.evaluate(expr)
        if text is Default or text is None:
            return text
        return str(text)

    def evaluateStructure(self, expr):
        return self.evaluate(expr)
    evaluateStructure = evaluate

    def evaluateMacro(self, expr):
        # XXX Should return None or a macro definition
        return self.evaluate(expr)
    evaluateMacro = evaluate

    def getTALESError(self):
        return TALESError

    def getDefault(self):
        return Default

    def setPosition(self, position):
        self.position = position

class SimpleExpr:
    '''Simple example of an expression type handler'''
    def __init__(self, name, expr, engine):
        self._name = name
        self._expr = expr
    def __call__(self, econtext):
        return self._name, self._expr
    def __repr__(self):
        return '<SimpleExpr %s %s>' % (self._name, `self._expr`)

