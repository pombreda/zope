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
$Id: testDictField.py,v 1.4 2002/07/17 16:54:15 jeremy Exp $
"""
from unittest import TestSuite, main, makeSuite
from Schema import Dict, Int, Float, ErrorNames
from testField import FieldTest

class DictTest(FieldTest):
    """Test the Dict Field."""

    def testValidate(self):
        field = Dict(id="field", title='Dict field',
                           description='', readonly=0, required=0)
        field.validate(None)
        field.validate({})
        field.validate({1: 'foo'})
        field.validate({'a': 1})
            
    def testValidateRequired(self):
        field = Dict(id="field", title='Dict field',
                           description='', readonly=0, required=1)
        field.validate({})
        field.validate({1: 'foo'})
        field.validate({'a': 1})
    
        self.assertRaisesErrorNames(ErrorNames.RequiredMissing,
                                    field.validate, None)

    def testValidateMinValues(self):
        field = Dict(id="field", title='Dict field',
                           description='', readonly=0, required=0,
                           min_values=1)    
        field.validate(None)
        field.validate({1: 'a'})
        field.validate({1: 'a', 2: 'b'})
    
        self.assertRaisesErrorNames(ErrorNames.NotEnoughElements,
                                    field.validate, {})

    def testValidateMaxValues(self):
        field = Dict(id="field", title='Dict field',
                           description='', readonly=0, required=0,
                           max_values=1)
        field.validate(None)
        field.validate({})
        field.validate({1: 'a'})
    
        self.assertRaisesErrorNames(ErrorNames.TooManyElements,
                                    field.validate, {1: 'a', 2: 'b'})
        self.assertRaisesErrorNames(ErrorNames.TooManyElements,
                                    field.validate, {1: 'a', 2: 'b', 3: 'c'})

    def testValidateMinValuesAndMaxValues(self):
        field = Dict(id="field", title='Dict field',
                           description='', readonly=0, required=0,
                           min_values=1, max_values=2)
        field.validate(None)
        field.validate({1: 'a'})
        field.validate({1: 'a', 2: 'b'})
    
        self.assertRaisesErrorNames(ErrorNames.NotEnoughElements,
                                    field.validate, {})
        self.assertRaisesErrorNames(ErrorNames.TooManyElements,
                                    field.validate, {1: 'a', 2: 'b', 3: 'c'})

    def testValidateValueTypes(self):
        field = Dict(id="field", title='Dict field',
                           description='', readonly=0, required=0,
                           value_types=(Int, Float))
        field.validate(None)
        field.validate({'a': 5.3})
        field.validate({'a': 2, 'b': 2.3})
        
        self.assertRaisesErrorNames(ErrorNames.WrongContainedType,
                                    field.validate, {1: ''} )
        self.assertRaisesErrorNames(ErrorNames.WrongContainedType,
                                    field.validate, {'a': ()} )

    def testValidateKeyTypes(self):
        field = Dict(id="field", title='Dict field',
                           description='', readonly=0, required=0,
                           key_types=(Int, Float))
        field.validate(None)
        field.validate({5.3: 'a'})
        field.validate({2: 'a', 2.3: 'b'})
    
        self.assertRaisesErrorNames(ErrorNames.WrongContainedType,
                                    field.validate, {'': 1} )
        self.assertRaisesErrorNames(ErrorNames.WrongContainedType,
                                    field.validate, {(): 'a'} )


def test_suite():
    return makeSuite(DictTest)

if __name__ == '__main__':
    main(defaultTest='test_suite')
