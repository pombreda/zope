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
$Id: testTupleField.py,v 1.3 2002/09/18 15:05:51 jim Exp $
"""
from unittest import TestSuite, main, makeSuite
from Zope.Schema import Tuple, Int, Float, ErrorNames
from testField import FieldTestBase

class TupleTest(FieldTestBase):
    """Test the Tuple Field."""

    def testValidate(self):
        field = Tuple(title=u'Tuple field', description=u'',
                      readonly=False, required=False)
        field.validate(None)
        field.validate(())
        field.validate((1, 2))
        field.validate((3,))
        
    def testValidateRequired(self):
        field = Tuple(title=u'Tuple field', description=u'',
                      readonly=False, required=True)
        field.validate(())
        field.validate((1, 2))
        field.validate((3,))

        self.assertRaisesErrorNames(ErrorNames.RequiredMissing,
                                    field.validate, None)

    def testValidateMinValues(self):
        field = Tuple(title=u'Tuple field', description=u'',
                      readonly=False, required=False, min_length=2)
        field.validate(None)
        field.validate((1, 2))
        field.validate((1, 2, 3))

        self.assertRaisesErrorNames(ErrorNames.TooShort,
                                    field.validate, ())
        self.assertRaisesErrorNames(ErrorNames.TooShort,
                                    field.validate, (1,))

    def testValidateMaxValues(self):
        field = Tuple(title=u'Tuple field', description=u'',
                      readonly=False, required=False, max_length=2)
        field.validate(None)
        field.validate(())
        field.validate((1, 2))

        self.assertRaisesErrorNames(ErrorNames.TooLong,
                                    field.validate, (1, 2, 3, 4))
        self.assertRaisesErrorNames(ErrorNames.TooLong,
                                    field.validate, (1, 2, 3))

    def testValidateMinValuesAndMaxValues(self):
        field = Tuple(title=u'Tuple field', description=u'',
                      readonly=False, required=False,
                      min_length=1, max_length=2)
        field.validate(None)
        field.validate((1, ))
        field.validate((1, 2))

        self.assertRaisesErrorNames(ErrorNames.TooShort,
                                    field.validate, ())
        self.assertRaisesErrorNames(ErrorNames.TooLong,
                                    field.validate, (1, 2, 3))

    def testValidateValueTypes(self):
        field = Tuple(title=u'Tuple field', description=u'',
                      readonly=False, required=False,
                      value_types=(Int(), Float()))
        field.validate(None)
        field.validate((5.3,))
        field.validate((2, 2.3))

        self.assertRaisesErrorNames(ErrorNames.WrongContainedType,
                                    field.validate, ('',) )
        self.assertRaisesErrorNames(ErrorNames.WrongContainedType,
                                    field.validate, (2, '') )

def test_suite():
    return makeSuite(TupleTest)

if __name__ == '__main__':
    main(defaultTest='test_suite')
