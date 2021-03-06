#############################################################################
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

import os
import posixpath
import sys

import zpkgsetup.setup


here = os.path.dirname(os.path.abspath(__file__))

def join(*parts):
    local_full_path = os.path.join(here, *parts)
    relative_path = posixpath.join(*parts)
    return local_full_path, relative_path


context = zpkgsetup.setup.SetupContext(
    "Zope", "3.1.0a42", __file__)

context.load_metadata(
    os.path.join(here, "releases", "Zope", "PUBLICATION.cfg"))

#context.scan("Zope",               *join("releases", "Zope"))
context.scan("BTrees",             *join("src", "BTrees"))
context.scan("persistent",         *join("src", "persistent"))
context.scan("ThreadedAsync",      *join("src", "ThreadedAsync"))
context.scan("transaction",        *join("src", "transaction"))
context.scan("ZConfig",            *join("src", "ZConfig"))
context.scan("zdaemon",            *join("src", "zdaemon"))
context.scan("ZEO",                *join("src", "ZEO"))
context.scan("ZODB",               *join("src", "ZODB"))
context.scan("zope",               *join("src", "zope"))
context.scan("zope.hookable",      *join("src", "zope", "hookable"))
context.scan("zope.i18nmessageid", *join("src", "zope", "i18nmessageid"))
context.scan("zope.interface",     *join("src", "zope", "interface"))
context.scan("zope.proxy",         *join("src", "zope", "proxy"))
context.scan("zope.security",      *join("src", "zope", "security"))
context.scan("zope.testing",       *join("src", "zope", "testing"))
context.scan("zope.thread",        *join("src", "zope", "thread"))
context.scan("zope.app.container", *join("src", "zope", "app", "container"))
context.setup()
