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
"""Document Template Tests

$Id: testdt_if.py,v 1.4 2003/05/01 19:35:41 faassen Exp $
"""

import unittest
from zope.documenttemplate.tests.dtmltestbase import DTMLTestBase

class TestDT_If(DTMLTestBase):


    def testBasic(self):

        html = self.doc_class(
            """\
             <dtml-if value>
               The arguments were: <dtml-var value>
             </dtml-if>
            """)

        result1 = "The arguments were: foo"
        result2 = ""

        self.assertEqual(html(value='foo').strip(), result1.strip())
        self.assertEqual(html().strip(), result2.strip())


    def testElse(self):

        html = self.doc_class(
            """\
             <dtml-if value>
               The arguments were: <dtml-var value>
             <dtml-else>
               No arguments were given.
             </dtml-if>
            """)

        result1 = "The arguments were: foo"
        result2 = "No arguments were given."

        self.assertEqual(html(value='foo').strip(), result1.strip())
        self.assertEqual(html().strip(), result2.strip())

    def testElIf(self):

        html = self.doc_class(
            """\
             <dtml-if value>
               The arguments were: <dtml-var value>
             <dtml-elif attribute>
               The attributes were: <dtml-var attribute>
             </dtml-if>
            """)

        result1 = "The arguments were: foo"
        result2 = "The attributes were: bar"

        self.assertEqual(html(value='foo', attribute='').strip(),
                         result1.strip())
        self.assertEqual(html(value='', attribute='bar').strip(),
                         result2.strip())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDT_If))
    return suite



if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
