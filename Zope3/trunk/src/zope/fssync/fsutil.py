##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""A few common items that don't fit elsewhere, it seems.

Classes:
- Error -- an exception

Functions:
- getoriginal(path)
- getextra(path)
- getannotations(path)
- getspecial(path, what)
- split(path)
- ensuredir(dir)

Variables:
- unwanted -- the tuple ("", os.curdir, os.pardir)
- nczope   -- the string os.path.normcase("@@Zope")

$Id: fsutil.py,v 1.2 2003/05/15 15:32:23 gvanrossum Exp $
"""

import os

class Error(Exception):
    """User-level error, e.g. non-existent file.

    This can be used in several ways:

        1) raise Error("message")
        2) raise Error("message %r %r" % (arg1, arg2))
        3) raise Error("message %r %r", arg1, arg2)
        4) raise Error("message", arg1, arg2)

    - Forms 2-4 are equivalent.

    - Form 4 assumes that "message" contains no % characters.

    - When using forms 2 and 3, all % formats are supported.

    - Form 2 has the disadvantage that when you specify a single
      argument that happens to be a tuple, it may get misinterpreted.

    - The message argument is required.

    - Any number of arguments after that is allowed.
    """

    def __init__(self, msg, *args):
        self.msg = msg
        self.args = args

    def __str__(self):
        msg, args = self.msg, self.args
        if args:
            if "%" in msg:
                msg = msg % args
            else:
                msg += " "
                msg += " ".join(map(repr, args))
        return str(msg)

    def __repr__(self):
        return "%s%r" % (self.__class__.__name__, (self.msg,)+self.args)

unwanted = ("", os.curdir, os.pardir)

nczope = os.path.normcase("@@Zope")

def getoriginal(path):
    """Return the path of the Original file corresponding to path."""
    return getspecial(path, "Original")

def getextra(path):
    """Return the path of the Extra directory corresponding to path."""
    return getspecial(path, "Extra")

def getannotations(path):
    """Return the path of the Annotations directory corresponding to path."""
    return getspecial(path, "Annotations")

def getspecial(path, what):
    """Helper for getoriginal(), getextra(), getannotations()."""
    head, tail = os.path.split(path)
    return os.path.join(head, "@@Zope", what, tail)

def split(path):
    """Split a path, making sure that the tail returned is real."""
    head, tail = os.path.split(path)
    if tail in unwanted:
        newpath = os.path.normpath(path)
        head, tail = os.path.split(newpath)
    if tail in unwanted:
        newpath = os.path.realpath(path)
        head, tail = os.path.split(newpath)
        if head == newpath or tail in unwanted:
            raise Error("path '%s' is the filesystem root", path)
    if not head:
        head = os.curdir
    return head, tail

def ensuredir(path):
    """Make sure that the given path is a directory, creating it if necessary.

    This may raise OSError if the creation operation fails.
    """
    if not os.path.isdir(path):
        os.makedirs(path)
