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
$Id: testBoolField.py,v 1.3 2002/07/17 16:54:15 jeremy Exp $
"""
from unittest import TestSuite, main, makeSuite
from Schema import Bool, ErrorNames
from testField import FieldTest

class BoolTest(FieldTest):
    """Test the Bool Field."""

    def testValidate(self):
        field = Bool(id="field", title='Bool field', description='',
                        readonly=0, required=0)        
        field.validate(None)
        field.validate(1)
        field.validate(0)
        field.validate(10)
        field.validate(-10)

    def testValidateRequired(self):
        field = Bool(id="field", title='Bool field', description='',
                        readonly=0, required=1)
        field.validate(1)
        field.validate(0)

        self.assertRaisesErrorNames(ErrorNames.RequiredMissing,
                                    field.validate, None)

    def testAllowedValues(self):
        field = Bool(id="field", title='Bool field', description='',
                        readonly=0, required=0, allowed_values=(0,))
        field.validate(None)
        field.validate(0)

        self.assertRaisesErrorNames(ErrorNames.InvalidValue,
                                    field.validate, 1)


def test_suite():
    return makeSuite(BoolTest)

if __name__ == '__main__':
    main(defaultTest='test_suite')
