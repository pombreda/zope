##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""DTML utilities

$Id$
"""
import re
import math
import random

from __builtin__ import str  # needed for pickling (legacy)
from types import ListType, StringType, TupleType

from zope.documenttemplate.pdocumenttemplate import \
     InstanceDict, TemplateDict, render_blocks


class ParseError(Exception):
    '''Document Template Parse Error'''

class ValidationError(Exception):
    '''Unauthorized'''


def html_quote(v, name='(Unknown name)', md={},
               character_entities=(
                       (('&'),    '&amp;'),
                       (('<'),    '&lt;' ),
                       (('>'),    '&gt;' ),
                       (('"'),    '&quot;'))): #"
    text = str(v)
    for re, name in character_entities:
        text = text.replace(re, name)
    return text


def int_param(params, md, name, default=0):
    try:
        v = params[name]
    except:
        v = default
    if v:
        try:
            v = v.atoi()
        except:
            v = md[v]
            if isinstance(v, StringType):
                v = v.atoi()
    return v or 0

_marker=[]

def careful_getattr(md, inst, name, default=_marker):

    if name[:1] != '_':

        try:
            v = getattr(inst, name)
        except:
            if default is not _marker:
                return default
            raise

        validate = md.validate

        if validate is None:
            return v

        if validate(inst, inst, name, v, md):
            return v

    raise ValidationError, name


def careful_hasattr(md, inst, name):
    v=getattr(inst, name, _marker)
    if v is not _marker:
        try:
            if name[:1] != '_':
                validate = md.validate
                if validate is None:
                    return 1

                if validate(inst, inst, name, v, md):
                    return 1
        except:
            pass
    return 0


def careful_getitem(md, mapping, key):
    v = mapping[key]
    if isinstance(v, StringType):
        return v # Short-circuit common case

    validate = md.validate
    if validate is None or validate(mapping, mapping, None, v, md):
        return v
    raise ValidationError, key


def careful_getslice(md, seq, *indexes):
    v = len(indexes)
    if v == 2:
        v = seq[indexes[0]:indexes[1]]
    elif v == 1:
        v = seq[indexes[0]:]
    else:
        v = seq[:]

    if isinstance(seq, StringType):
        return v # Short-circuit common case

    validate = md.validate
    if validate is not None:
        for e in v:
            if not validate(seq,seq,None,e,md):
                raise ValidationError, u'unauthorized access to slice member'

    return v


def careful_range(md, iFirst, *args):
    # limited range function from Martijn Pieters
    RANGELIMIT = 1000
    if not len(args):
        iStart, iEnd, iStep = 0, iFirst, 1
    elif len(args) == 1:
        iStart, iEnd, iStep = iFirst, args[0], 1
    elif len(args) == 2:
        iStart, iEnd, iStep = iFirst, args[0], args[1]
    else:
        raise AttributeError, u'range() requires 1-3 int arguments'
    if iStep == 0:
        raise ValueError, u'zero step for range()'
    iLen = int((iEnd - iStart) / iStep)
    if iLen < 0:
        iLen = 0
    if iLen >= RANGELIMIT:
        raise ValueError, u'range() too large'
    return range(iStart, iEnd, iStep)


d = TemplateDict.__dict__
for name in ('None', 'abs', 'chr', 'divmod', 'float', 'hash', 'hex', 'int',
             'len', 'max', 'min', 'oct', 'ord', 'round', 'str'):
    d[name] = __builtins__[name]

d['math'] = math
d['random'] = random

def careful_pow(self, x, y, z):
    if not z:
        raise ValueError, 'pow(x, y, z) with z==0'
    return pow(x,y,z)

d['pow'] = careful_pow

try:
    import DateTime
    d['DateTime']=DateTime.DateTime
except:
    pass


def test(self, *args):
    l = len(args)
    for i in range(1, l, 2):
        if args[i-1]:
            return args[i]

    if l%2:
        return args[-1]

d['test'] = test

def obsolete_attr(self, inst, name, md):
    return careful_getattr(md, inst, name)

d['attr'] = obsolete_attr
d['getattr'] = careful_getattr
d['hasattr'] = careful_hasattr
d['range'] = careful_range

def namespace(self, **kw):
    """Create a tuple consisting of a single instance whose attributes are
    provided as keyword arguments."""
    if getattr(self, '__class__', None) != TemplateDict:
        raise TypeError,'''A call was made to DT_Util.namespace() with an
        incorrect "self" argument.  It could be caused by a product which
        is not yet compatible with this version of Zope.  The traceback
        information may contain more details.)'''
    return apply(self, (), kw)

d['namespace'] = namespace

def render(self, v):
    "Render an object in the way done by the 'name' attribute"
    if hasattr(v, '__render_with_namespace__'):
        v = v.__render_with_namespace__(self)
    else:
        vbase = getattr(v, 'aq_base', v)
        if callable(vbase):
            v = v()
    return v

d['render'] = render

def reorder(self, s, with=None, without=()):
    if with is None:
        with = s
    d = {}
    for i in s:
        if isinstance(i, TupleType) and len(i) == 2:
            k, v = i
        else:
            k = v = i
        d[k] = v
    r = []
    a = r.append
    h = d.has_key

    for i in without:
        if isinstance(i, TupleType) and len(i) == 2:
            k, v = i
        else:
            k= v = i
        if h(k):
            del d[k]

    for i in with:
        if isinstance(i, TupleType) and len(i) == 2:
            k, v = i
        else:
            k= v = i
        if h(k):
            a((k,d[k]))
            del d[k]

    return r

d['reorder'] = reorder


class Eval:

    def __init__(self, expr):

        expr = expr.strip()
        expr = expr.replace('\n', ' ')
        expr = expr.replace('\r', ' ')
        self.expr = expr
        self.code = compile(expr,'<string>','eval')


    def eval(self, mapping):
        d={'_vars': mapping,
           '_': mapping}
        code = self.code
        for name in code.co_names:
            if not d.has_key(name):
                __traceback_info__ = name
                try:
                    d[name] = mapping.getitem(name, 0)
                except KeyError:
                    # Swallow KeyErrors since the expression
                    # might not actually need the name.  If it
                    # does need the name, a NameError will occur.
                    pass

        return eval(code, {}, d)


    def __call__(self, **kw):
        return eval(self.code, {}, kw)



def name_param(params,tag='',expr=0, attr='name', default_unnamed=1):
    used = params.has_key
    __traceback_info__ = params, tag, expr, attr

    #if expr and used('expr') and used('') and not used(params['']):
    #   # Fix up something like: <!--#in expr="whatever" mapping-->
    #   params[params['']]=default_unnamed
    #   del params['']

    if used(''):
        v = params['']

        if v[:1] == '"' and v[-1:] == '"' and len(v) > 1: # expr shorthand
            if used(attr):
                raise ParseError, (u'%s and expr given' % attr, tag)
            if expr:
                if used('expr'):
                    raise ParseError, (u'two exprs given', tag)
                v = v[1:-1]
                try:
                    expr=Eval(v)
                except SyntaxError, v:
                    raise ParseError, (
                        u'<strong>Expression (Python) Syntax error</strong>:'
                        u'\n<pre>\n%s\n</pre>\n' % v[0],
                        tag)
                return v, expr
            else:
                raise ParseError, (
                    u'The "..." shorthand for expr was used in a tag '
                    u'that doesn\'t support expr attributes.',
                    tag)

        else: # name shorthand
            if used(attr):
                raise ParseError, (u'Two %s values were given' % attr, tag)
            if expr:
                if used('expr'):
                    # raise 'Waaaaaa', 'waaa'
                    raise ParseError, (u'%s and expr given' % attr, tag)
                return params[''],None
            return params['']

    elif used(attr):
        if expr:
            if used('expr'):
                raise ParseError, (u'%s and expr given' % attr, tag)
            return params[attr],None
        return params[attr]
    elif expr and used('expr'):
        name = params['expr']
        expr = Eval(name)
        return name, expr

    raise ParseError, (u'No %s given' % attr, tag)


Expr_doc = u"""
Python expression support

  Several document template tags, including 'var', 'in', 'if', 'else',
  and 'elif' provide support for using Python expressions via an
  'expr' tag attribute.

  Expressions may be used where a simple variable value is
  inadequate.  For example, an expression might be used to test
  whether a variable is greater than some amount::

     <dtml-if expr="age > 18">

  or to transform some basic data::

     <dtml-var expr="phone[:3]">

  Objects available in the document templates namespace may be used.
  Subobjects of these objects may be used as well, although subobject
  access is restricted by the optional validation method.

  In addition, a special additional name, '_', is available.  The '_'
  variable provides access to the document template namespace as a
  mapping object.  This variable can be useful for accessing objects
  in a document template namespace that have names that are not legal
  Python variable names::

     <dtml-var expr="_['sequence-number']*5">

  This variable also has attributes that provide access to standard
  utility objects.  These attributes include:

  - The objects: 'None', 'abs', 'chr', 'divmod', 'float', 'hash',
       'hex', 'int', 'len', 'max', 'min', 'oct', 'ord', 'pow',
       'round', and 'str' from the standard Python builtin module.

  - Special security-aware versions of 'getattr' and 'hasattr',

  - The Python 'string', 'math', and 'random' modules, and

  - A special function, 'test', that supports if-then expressions.
    The 'test' function accepts any number of arguments.  If the
    first argument is true, then the second argument is returned,
    otherwise if the third argument is true, then the fourth
    argument is returned, and so on.  If there is an odd number of
    arguments, then the last argument is returned in the case that
    none of the tested arguments is true, otherwise None is
    returned.

  For example, to convert a value to lower case::

    <dtml-var expr="title.lower()">

"""


def parse_params(text,
                 result=None,
                 tag='',
                 unparmre=re.compile('([\000- ]*([^\000- ="]+))'),
                 qunparmre=re.compile('([\000- ]*("[^"]*"))'),
                 parmre=re.compile('([\000- ]*([^\000- ="]+)=([^\000- ="]+))'),
                 qparmre=re.compile('([\000- ]*([^\000- ="]+)="([^"]*)")'),
                 **parms):

    """Parse tag parameters

    The format of tag parameters consists of 1 or more parameter
    specifications separated by whitespace.  Each specification
    consists of an unnamed and unquoted value, a valueless name, or a
    name-value pair.  A name-value pair consists of a name and a
    quoted or unquoted value separated by an '='.

    The input parameter, text, gives the text to be parsed.  The
    keyword parameters give valid parameter names and default values.

    If a specification is not a name-value pair and it is not the
    first specification and it is a
    valid parameter name, then it is treated as a name-value pair with
    a value as given in the keyword argument.  Otherwise, if it is not
    a name-value pair, it is treated as an unnamed value.

    The data are parsed into a dictionary mapping names to values.
    Unnamed values are mapped from the name '""'.  Only one value may
    be given for a name and there may be only one unnamed value. """

    result = result or {}

    # HACK - we precalculate all matches. Maybe we don't need them
    # all. This should be fixed for performance issues

    mo_p = parmre.match(text)
    mo_q = qparmre.match(text)
    mo_unp = unparmre.match(text)
    mo_unq = qunparmre.match(text)

    if mo_p:
        name = mo_p.group(2).lower()
        value = mo_p.group(3)
        l = len(mo_p.group(1))
    elif mo_q:
        name = mo_q.group(2).lower()
        value = mo_q.group(3)
        l = len(mo_q.group(1))
    elif mo_unp:
        name = mo_unp.group(2)
        l = len(mo_unp.group(1))
        if result:
            if parms.has_key(name):
                if parms[name] is None: raise ParseError, (
                    u'Attribute %s requires a value' % name, tag)

                result[name] = parms[name]
            else: raise ParseError, (
                u'Invalid attribute name, "%s"' % name, tag)
        else:
            result[''] = name
        return apply(parse_params, (text[l:],result), parms)
    elif mo_unq:
        name = mo_unq.group(2)
        l = len(mo_unq.group(1))
        if result:
            raise ParseError, (u'Invalid attribute name, "%s"' % name, tag)
        else:
            result[''] = name
        return apply(parse_params, (text[l:], result), parms)
    else:
        if not text or not text.strip():
            return result
        raise ParseError, (u'invalid parameter: "%s"' % text, tag)

    if not parms.has_key(name):
        raise ParseError, (u'Invalid attribute name, "%s"' % name, tag)

    if result.has_key(name):
        p = parms[name]
        if type(p) is not ListType or p:
            raise ParseError, (
                u'Duplicate values for attribute "%s"' % name, tag)

    result[name] = value

    text = text[l:].strip()
    if text:
        return apply(parse_params, (text,result), parms)
    else:
        return result
