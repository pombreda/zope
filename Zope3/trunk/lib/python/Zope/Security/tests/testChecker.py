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

Revision information:
$Id: testChecker.py,v 1.3 2002/07/17 16:54:23 jeremy Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Security.Checker import NamesChecker, CheckerPublic
from Zope.Testing.CleanUp import cleanUp
from Zope.Security.ISecurityPolicy import ISecurityPolicy
from Zope.Exceptions import Forbidden, Unauthorized
from Zope.Security.SecurityManagement import setSecurityPolicy
from Zope.Security.Proxy import getChecker, getObject
from Zope.Security.Checker import defineChecker

class SecurityPolicy:

    __implements__ =  ISecurityPolicy

    ############################################################
    # Implementation methods for interface
    # Zope.Security.ISecurityPolicy.

    def checkPermission(self, permission, object, context):
        'See Zope.Security.ISecurityPolicy.ISecurityPolicy'

        return permission == 'test_allowed'

    #
    ############################################################


class OldInst:
    a=1
    
    def b(self):
        pass
    
    c=2

    def gete(self): return 3
    e = property(gete)

    def __getitem__(self, x): return 5, x

    def __setitem__(self, x, v): pass

class NewInst(object, OldInst):

    def gete(self): return 3
    def sete(self, v): pass
    e = property(gete, sete)

class Test(TestCase):

    def setUp(self):
        self.__oldpolicy = setSecurityPolicy(SecurityPolicy())

    def tearDown(self):
        setSecurityPolicy(self.__oldpolicy)
        cleanUp()


    # check_getattr cases:
    #
    # - no attribute there
    # - method
    # - allow and disallow by permission
    def test_check_getattr(self):        

        oldinst = OldInst()
        oldinst.d = OldInst()

        newinst = NewInst()
        newinst.d = NewInst()

        for inst in oldinst, newinst:
            checker = NamesChecker(['a', 'b', 'c', '__getitem__'],
                                   'perm')

            self.assertRaises(Unauthorized, checker.check_getattr, inst, 'a')
            self.assertRaises(Unauthorized, checker.check_getattr, inst, 'b')
            self.assertRaises(Unauthorized, checker.check_getattr, inst, 'c')
            self.assertRaises(Unauthorized, checker.check, inst, '__getitem__')
            self.assertRaises(Forbidden, checker.check, inst, '__setitem__')
            self.assertRaises(Forbidden, checker.check_getattr, inst, 'd')
            self.assertRaises(Forbidden, checker.check_getattr, inst, 'e')
            self.assertRaises(Forbidden, checker.check_getattr, inst, 'f')

            checker = NamesChecker(['a', 'b', 'c', '__getitem__'],
                                   'test_allowed')

            checker.check_getattr(inst, 'a')
            checker.check_getattr(inst, 'b')
            checker.check_getattr(inst, 'c')
            checker.check(inst, '__getitem__')
            self.assertRaises(Forbidden, checker.check, inst, '__setitem__')
            self.assertRaises(Forbidden, checker.check_getattr, inst, 'd')
            self.assertRaises(Forbidden, checker.check_getattr, inst, 'e')
            self.assertRaises(Forbidden, checker.check_getattr, inst, 'f')

    def test_proxy(self):
        checker = NamesChecker(())


        for rock in (1, 1.0, 1l, 1j,
                     '1', u'1', None,
                     AttributeError, AttributeError(),
                     ):
            proxy = checker.proxy(rock)
            
            self.failUnless(proxy is rock, (rock, type(proxy)))

        for class_ in OldInst, NewInst:
            inst = class_()

            for ob in inst, class_:
                proxy = checker.proxy(ob)
                self.failUnless(getObject(proxy) is ob)
                checker = getChecker(proxy)
                if ob is inst:
                    self.assertEqual(checker.permission_id('__str__'),
                                     None)
                else:
                    self.assertEqual(checker.permission_id('__str__'),
                                     CheckerPublic)
        
            special = NamesChecker(['a', 'b'], 'test_allowed')
            defineChecker(class_, special)

            proxy = checker.proxy(inst)
            self.failUnless(getObject(proxy) is inst)

                
            checker = getChecker(proxy)
            self.failUnless(checker is special, checker.__dict__)

            proxy2 = checker.proxy(proxy)
            self.failUnless(proxy2 is proxy, [proxy, proxy2])

    def testMultiChecker(self):
        from Interface import Interface

        class I1(Interface):
            def f1(): ''
            def f2(): ''

        class I2(I1):
            def f3(): ''
            def f4(): ''

        class I3(Interface):
            def g(): ''

        from Zope.Exceptions import DuplicationError

        from Zope.Security.Checker import MultiChecker

        self.assertRaises(DuplicationError,
                          MultiChecker,
                          [(I1, 'p1'), (I2, 'p2')])

        self.assertRaises(DuplicationError,
                          MultiChecker,
                          [(I1, 'p1'), {'f2': 'p2'}])

        MultiChecker([(I1, 'p1'), (I2, 'p1')])

        checker = MultiChecker([
            (I2, 'p1'),
            {'a': 'p3'},
            (I3, 'p2'),
            (('x','y','z'), 'p4'),
            ])

        self.assertEqual(checker.permission_id('f1'), 'p1')
        self.assertEqual(checker.permission_id('f2'), 'p1')
        self.assertEqual(checker.permission_id('f3'), 'p1')
        self.assertEqual(checker.permission_id('f4'), 'p1')
        self.assertEqual(checker.permission_id('g'), 'p2')
        self.assertEqual(checker.permission_id('a'), 'p3')
        self.assertEqual(checker.permission_id('x'), 'p4')
        self.assertEqual(checker.permission_id('y'), 'p4')
        self.assertEqual(checker.permission_id('z'), 'p4')
        self.assertEqual(checker.permission_id('zzz'), None)
            
    def testNonPrivateChecker(self):
        from Zope.Security.Checker import NonPrivateChecker
        checker = NonPrivateChecker('p')
        self.assertEqual(checker.permission_id('z'), 'p')
        self.assertEqual(checker.permission_id('_z'), None)
            
    def testAlwaysAvailable(self):
        from Zope.Security.Checker import NamesChecker
        checker = NamesChecker(())
        class C: pass
        self.assertEqual(checker.check(C, '__hash__'), None)
        self.assertEqual(checker.check(C, '__nonzero__'), None)
        self.assertEqual(checker.check(C, '__class__'), None)
        self.assertEqual(checker.check(C, '__implements__'), None)
        self.assertEqual(checker.check(C, '__lt__'), None)
        self.assertEqual(checker.check(C, '__le__'), None)
        self.assertEqual(checker.check(C, '__gt__'), None)
        self.assertEqual(checker.check(C, '__ge__'), None)
        self.assertEqual(checker.check(C, '__eq__'), None)
        self.assertEqual(checker.check(C, '__ne__'), None)

    def test_setattr(self):
        checker = NamesChecker(['a', 'b', 'c', '__getitem__'],
                               'test_allowed')

        for inst in NewInst(), OldInst():
            self.assertRaises(Forbidden, checker.check_setattr, inst, 'a')
            self.assertRaises(Forbidden, checker.check_setattr, inst, 'z')



def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')








