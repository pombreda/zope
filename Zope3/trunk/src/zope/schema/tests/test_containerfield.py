##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""
$Id: test_containerfield.py,v 1.1 2003/01/25 02:49:27 rdmurray Exp $
"""
from UserDict import UserDict
from unittest import TestSuite, main, makeSuite
from zope.schema import Container
from zope.schema.errornames import RequiredMissing, NotAContainer
from zope.schema.tests.test_field import FieldTestBase

class ContainerTest(FieldTestBase):
    """Test the Container Field."""

    _Field_Factory = Container

    def testValidate(self):
        field = self._Field_Factory(title=u'test field', description=u'',
                                    readonly=False, required=False)
        field.validate(None)
        field.validate('')
        field.validate('abc')
        field.validate([1, 2, 3])
        field.validate({'a': 1, 'b': 2})
        field.validate(UserDict())

        self.assertRaisesErrorNames(NotAContainer, field.validate, 1)
        self.assertRaisesErrorNames(NotAContainer, field.validate, True)

    def testValidateRequired(self):
        field = self._Field_Factory(title=u'test field', description=u'',
                                    readonly=False, required=True)

        field.validate('')

        self.assertRaisesErrorNames(RequiredMissing, field.validate, None)


def test_suite():
    return makeSuite(ContainerTest)

if __name__ == '__main__':
    main(defaultTest='test_suite')
