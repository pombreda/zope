##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
"""
Copy a DOM tree, applying TAL (Template Attribute Language) transformations.
"""

import string
import re
from xml.dom import Node
from CopyingDOMVisitor import CopyingDOMVisitor

ZOPE_TAL_NS = "http://xml.zope.org/namespaces/tal"
ZOPE_METAL_NS = "http://xml.zope.org/namespaces/metal"

NAME_RE = "[a-zA-Z_][a-zA-Z0-9_]*"

class TALVisitor(CopyingDOMVisitor):

    """
    Copy a DOM tree while applying TAL transformations.

    The DOM tree must have been created with XML namespace information
    included (i.e. I'm not going to interpret your xmlns* attributes
    for you), otherwise we will make an unmodified copy.
    """

    def __init__(self, document, documentFactory, engine):
        CopyingDOMVisitor.__init__(self, document, documentFactory)
        self.document = document
        self.engine = engine
        self.currentMacro = None
        self.originalNode = None
        self.slotIndex = None

    def visitElement(self, node):
        if not node.hasAttributes():
            CopyingDOMVisitor.visitElement(self, node)
            return
        macroName = node.getAttributeNS(ZOPE_METAL_NS, "use-macro")
        if macroName:
            macroNode = self.findMacro(macroName)
            if macroNode:
                self.expandMacro(macroNode, node)
            return
        if self.currentMacro and self.slotIndex and self.originalNode:
            slotName = node.getAttributeNS(ZOPE_METAL_NS, "define-slot")
            if slotName:
                slotNode = self.slotIndex.get(slotName)
                if slotNode:
                    self.visitElement(slotNode)
                    return
        defines = node.getAttributeNS(ZOPE_TAL_NS, "define")
        if defines:
            self.engine.beginScope()
            self.doDefine(defines)
            self.finishElement(node)
            self.engine.endScope()
        else:
            self.finishElement(node)

    def finishElement(self, node):
        condition = node.getAttributeNS(ZOPE_TAL_NS, "condition")
        if condition and not self.engine.evaluateBoolean(condition):
            return
        attrDict = {}
        attributes = node.getAttributeNS(ZOPE_TAL_NS, "attributes")
        if attributes:
            attrDict = parseAttributeReplacements(attributes)
        insert = node.getAttributeNS(ZOPE_TAL_NS, "insert")
        replace = node.getAttributeNS(ZOPE_TAL_NS, "replace")
        repeat = node.getAttributeNS(ZOPE_TAL_NS, "repeat")
        n = 0
        if insert: n = n+1
        if replace: n = n+1
        if repeat: n = n+1
        if n > 1:
            print "Please use only one of z:insert, z:replace, z:repeat"
        ok = 0
        if insert:
            ok = self.doInsert(node, insert, attrDict)
        if not ok and replace:
            # XXX Check that this isn't the documentElement
            ok = self.doReplace(node, replace, attrDict)
        if not ok and repeat:
            # XXX Check that this isn't the documentElement
            ok = self.doRepeat(node, repeat, attrDict)
        if not ok:
            self.copySubtree(node, attrDict)

    def findMacro(self, macroName):
        # XXX This is not written for speed :-)
        doc, localName = self.engine.findMacroDocument(macroName)
        if not doc:
            doc = self.document
        macroDict = macroIndexer(doc)
        if macroDict.has_key(localName):
            return macroDict[localName]
        else:
            print "No macro found:", macroName
            return None

    def expandMacro(self, macroNode, originalNode):
        save = self.currentMacro, self.slotIndex, self.originalNode
        self.currentMacro = macroNode
        self.slotIndex = slotIndexer(originalNode)
        self.originalNode = originalNode
        self.visitElement(macroNode)
        self.currentMacro, self.slotIndex, self.originalNode = save

    def doDefine(self, arg):
        for part in splitParts(arg):
            m = re.match(
                r"\s*(?:(global|local)\s+)?(%s)\s+(.*)" % NAME_RE, part)
            if not m:
                print "Bad syntax in z:define argument:", `part`
            else:
                scope, name, expr = m.group(1, 2, 3)
                scope = scope or "local"
                value = self.engine.evaluateValue(expr)
                if scope == "local":
                    self.engine.setLocal(name, value)
                else:
                    self.engine.setGlobal(name, value)

    def doInsert(self, node, arg, attrDict):
        key, expr = parseSubstitution(arg)
        if not key:
            return 0
        self.copyElement(node)
        self.copyAttributes(node, attrDict)
        self.doSubstitution(key, expr, {})
        self.backUp()
        return 1

    def doReplace(self, node, arg, attrDict):
        key, expr = parseSubstitution(arg)
        if not key:
            return 0
        self.doSubstitution(key, expr, attrDict)
        return 1

    def doSubstitution(self, key, expr, attrDict):
        if key == "text":
            if attrDict:
                print "Warning: z:attributes unused for text replacement"
            data = self.engine.evaluateText(expr)
            newChild = self.newDocument.createTextNode(str(data))
            self.curNode.appendChild(newChild)
        elif key == "structure":
            # XXX need to copy the nodes
            data = self.engine.evaluateStructure(expr)
            # XXX maybe data needs to be a documentFragment node;
            # then the implementation here isn't quite right
            attrDone = not attrDict
            for newChild in data:
                self.curNode.appendChild(newChild)
                if not attrDone and newChild.nodeType == Node.ELEMENT_NODE:
                    self.changeAttributes(newChild, attrDict)
                    attrDone = 1
            if not attrDone:
                # Apparently no element nodes were inserted
                print "Warning: z:attributes unused for struct replacement"

    def doRepeat(self, node, arg, attrDict):
        if not self.newDocument:
            print "Can't have z:repeat on the documentElement"
            return 0
        m = re.match("\s*(%s)\s+(.*)" % NAME_RE, arg)
        if not m:
            print "Bad syntax in z:repeat:", `arg`
            return 0
        name, expr = m.group(1, 2)
        iterator = self.engine.setupLoop(name, expr)
        while iterator.next():
            self.copySubtree(node, attrDict)
        return 1

    def copySubtree(self, node, attrDict):
        self.copyElement(node)
        self.copyAttributes(node, attrDict)
        self.visitAllChildren(node)
        self.backUp()

    def copyAttributes(self, node, attrDict):
        for attr in node.attributes.values():
            namespaceURI = attr.namespaceURI
            attrName = attr.nodeName
            attrValue = attr.nodeValue
            if attrDict.has_key(attrName):
                expr = attrDict[attrName]
                if expr == "nothing":
                    continue
                attrValue = self.engine.evaluateText(expr)
                if attrValue is None:
                    continue
            if namespaceURI:
                # When expanding a macro, change its define-macro to use-macro
                if (self.currentMacro and
                    namespaceURI == ZOPE_METAL_NS and
                    attr.localName == "define-macro"):
                    attrName = attr.prefix + ":use-macro"
                self.curNode.setAttributeNS(namespaceURI, attrName, attrValue)
            else:
                self.curNode.setAttribute(attrName, attrValue)

def parseAttributeReplacements(arg):
    dict = {}
    for part in splitParts(arg):
        m = re.match(r"\s*([^\s]+)\s*(.*)", part)
        if not m:
            print "Bad syntax in z:attributes:", `part`
            continue
        name, expr = m.group(1, 2)
        if dict.has_key(name):
            print "Duplicate attribute name in z:attributes:", `part`
            continue
        dict[name] = expr
    return dict

def parseSubstitution(arg):
    m = re.match(r"\s*(?:(text|structure)\s+)?(.*)", arg)
    if not m:
        print "Bad syntax in z:insert/replace:", `arg`
        return None, None
    key, expr = m.group(1, 2)
    if not key:
        key = "text"
    return key, expr

def splitParts(arg):
    # Break in pieces at undoubled semicolons and
    # change double semicolons to singles:
    arg = string.replace(arg, ";;", "\0")
    parts = string.split(arg, ';')
    parts = map(lambda s: string.replace(s, "\0", ";;"), parts)
    return parts


def macroIndexer(document):
    """
    Return a dictionary containing all define-macro nodes in a document.

    The dictionary will have the form {macroName: node, ...}.
    """
    macroIndex = {}
    _macroVisitor(document.documentElement, macroIndex)
    return macroIndex

def _macroVisitor(node, macroIndex, __elementNodeType=Node.ELEMENT_NODE):
    # Internal routine to efficiently recurse down the tree of elements
    macroName = node.getAttributeNS(ZOPE_METAL_NS, "define-macro")
    if macroName:
        if macroIndex.has_key(macroName):
            print ("Duplicate macro definition: %s in <%s>" %
                   (macroName, node.nodeName))
        else:
            macroIndex[macroName] = node
    for child in node.childNodes:
        if child.nodeType == __elementNodeType:
            _macroVisitor(child, macroIndex)


def slotIndexer(rootNode):
    """
    Return a dictionary containing all fill-slot nodes in a subtree.

    The dictionary will have the form {slotName: node, ...}.
    """
    slotIndex = {}
    _slotVisitor(rootNode, slotIndex)
    return slotIndex

def _slotVisitor(node, slotIndex, __elementNodeType=Node.ELEMENT_NODE):
    # Internal routine to efficiently recurse down the tree of elements
    slotName = node.getAttributeNS(ZOPE_METAL_NS, "fill-slot")
    if slotName:
        if slotIndex.has_key(slotName):
            print ("Duplicate slot definition: %s in <%s>" %
                   (slotName, node.nodeName))
        else:
            slotIndex[slotName] = node
    for child in node.childNodes:
        if child.nodeType == __elementNodeType:
            _slotVisitor(child, slotIndex)
