##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: testGlobalBrowserMenuServiceDirectives.py,v 1.1 2002/06/18 19:34:57 jim Exp $
"""

import os
from StringIO import StringIO
from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Configuration.xmlconfig import xmlconfig
from Zope.Publisher.Browser.IBrowserPublisher import IBrowserPublisher
from Zope.Publisher.Browser.BrowserRequest import TestRequest
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup

import Zope.App.Publisher.Browser
defs_path = os.path.join(
    os.path.split(Zope.App.Publisher.Browser.__file__)[0],
    'meta.zcml')

template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:browser='http://namespaces.zope.org/browser'>
   %s
   </zopeConfigure>"""

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        xmlconfig(open(defs_path))
        
    def test(self):
        from Zope.App.Publisher.Browser.GlobalBrowserMenuService \
             import globalBrowserMenuService
        
        xmlconfig(StringIO(template % (
            """
            <browser:menu id="test_id" title="test menu" />

            <browser:menuItems menu="test_id" for="Interface.Interface">
              <browser:menuItem action="a1" title="t1" />
            </browser:menuItems>

            <browser:menuItems menu="test_id"
              for="
           Zope.App.Publisher.Browser.tests.testGlobalBrowserMenuService.I1
              ">
              <browser:menuItem action="a2" title="t2" />
            </browser:menuItems>

            <browser:menuItems menu="test_id"
              for="
           Zope.App.Publisher.Browser.tests.testGlobalBrowserMenuService.I11
              ">
              <browser:menuItem action="a3" title="t3" filter="context" />
              <browser:menuItem action="a4" title="t4" filter="not:context" />
            </browser:menuItems>

            <browser:menuItems menu="test_id"
              for="
           Zope.App.Publisher.Browser.tests.testGlobalBrowserMenuService.I111
              ">
              <browser:menuItem action="a5" title="t5" />
              <browser:menuItem action="a6" title="t6" />
              <browser:menuItem action="f7" title="t7" />
              <browser:menuItem action="u8" title="t8" />
            </browser:menuItems>

            <browser:menuItems menu="test_id"
              for="
           Zope.App.Publisher.Browser.tests.testGlobalBrowserMenuService.I12
              ">
              <browser:menuItem action="a9" title="t9" />
            </browser:menuItems>
            """)))


        from Zope.App.Publisher.Browser.tests.testGlobalBrowserMenuService \
             import X

        menu = globalBrowserMenuService.getMenu('test_id', X(), TestRequest())

        def d(n):
            return {'action': "a%s" % n,
                    'title':  "t%s" % n,
                    'description':  "",
                    }
        
        self.assertEqual(list(menu), [d(5), d(6), d(3), d(2), d(1)])


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
