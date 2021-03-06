##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for TypesTool module.

$Id$
"""

import unittest
import Testing

import Products
from AccessControl import Unauthorized
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from Acquisition import aq_base
from Products.Five import zcml
from Products.PythonScripts.PythonScript import PythonScript
from Products.PythonScripts.standard import html_quote
from webdav.NullResource import NullResource

from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.tests.base.dummy import DummyFactory
from Products.CMFCore.tests.base.dummy import DummyFolder
from Products.CMFCore.tests.base.dummy import DummyObject
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyUserFolder
from Products.CMFCore.tests.base.security import OmnipotentUser
from Products.CMFCore.tests.base.security import UserWithRoles
from Products.CMFCore.tests.base.testcase import _TRAVERSE_ZCML
from Products.CMFCore.tests.base.testcase import PlacelessSetup
from Products.CMFCore.tests.base.testcase import SecurityTest
from Products.CMFCore.tests.base.testcase import WarningInterceptor
from Products.CMFCore.tests.base.tidata import FTIDATA_ACTIONS
from Products.CMFCore.tests.base.tidata import FTIDATA_CMF15
from Products.CMFCore.tests.base.tidata import FTIDATA_DUMMY
from Products.CMFCore.tests.base.tidata import STI_SCRIPT


class TypesToolTests(PlacelessSetup, SecurityTest, WarningInterceptor):

    def _makeOne(self):
        from Products.CMFCore.TypesTool import TypesTool

        return TypesTool()

    def setUp( self ):
        from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI

        PlacelessSetup.setUp(self)
        SecurityTest.setUp(self)
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('permissions.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.Five.browser)
        zcml.load_config('configure.zcml', Products.CMFCore)
        zcml.load_string(_TRAVERSE_ZCML)

        self.site = DummySite('site').__of__(self.root)
        self.acl_users = self.site._setObject( 'acl_users', DummyUserFolder() )
        self.ttool = self.site._setObject( 'portal_types', self._makeOne() )
        fti = FTIDATA_DUMMY[0].copy()
        self.ttool._setObject( 'Dummy Content', FTI(**fti) )

    def tearDown(self):
        SecurityTest.tearDown(self)
        PlacelessSetup.tearDown(self)
        self._free_warning_output()

    def test_z2interfaces(self):
        from Interface.Verify import verifyClass
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider
        from Products.CMFCore.interfaces.portal_types \
                import portal_types as ITypesTool
        from Products.CMFCore.TypesTool import TypesTool

        verifyClass(IActionProvider, TypesTool)
        verifyClass(ITypesTool, TypesTool)

    def test_z3interfaces(self):
        from zope.interface.verify import verifyClass
        from Products.CMFCore.interfaces import IActionProvider
        from Products.CMFCore.interfaces import ITypesTool
        from Products.CMFCore.TypesTool import TypesTool

        verifyClass(IActionProvider, TypesTool)
        verifyClass(ITypesTool, TypesTool)

    def test_allMetaTypes(self):
        """
        Test that everything returned by allMetaTypes can be
        traversed to.
        """
        tool = self.ttool
        meta_types={}
        # Seems we get NullResource if the method couldn't be traverse to
        # so we check for that. If we've got it, something is b0rked.
        for factype in tool.all_meta_types():
            meta_types[factype['name']]=1
            # The html_quote below is necessary 'cos of the one in
            # main.dtml. Could be removed once that is gone.
            act = tool.unrestrictedTraverse(html_quote(factype['action']))
            self.failIf(type(aq_base(act)) is NullResource)

        # Check the ones we're expecting are there
        self.failUnless(meta_types.has_key('Scriptable Type Information'))
        self.failUnless(meta_types.has_key('Factory-based Type Information'))

    def test_constructContent(self):
        from Products.CMFCore.TypesTool \
                import ScriptableTypeInformation as STI

        site = self.site
        acl_users = self.acl_users
        ttool = self.ttool
        setSecurityPolicy(self._oldPolicy)
        newSecurityManager(None, acl_users.all_powerful_Oz)
        self.site._owner = (['acl_users'], 'all_powerful_Oz')
        sti_baz = STI('Baz',
                      permission='Add portal content',
                      constructor_path='addBaz')
        ttool._setObject('Baz', sti_baz)
        ttool._setObject( 'addBaz',  PythonScript('addBaz') )
        s = ttool.addBaz
        s.write(STI_SCRIPT)

        f = site._setObject( 'folder', PortalFolder(id='folder') )
        f.manage_addProduct = { 'FooProduct' : DummyFactory(f) }
        f._owner = (['acl_users'], 'user_foo')
        self.assertEqual( f.getOwner(), acl_users.user_foo )

        ttool.constructContent('Dummy Content', container=f, id='page1')
        try:
            ttool.constructContent('Baz', container=f, id='page2')
        except Unauthorized:
            self.fail('CMF Collector issue #165 (Ownership bug): '
                      'Unauthorized raised' )


class TypeInfoTests(unittest.TestCase):

    def _makeTypesTool(self):
        from Products.CMFCore.TypesTool import TypesTool

        return TypesTool()

    def test_construction( self ):
        ti = self._makeInstance( 'Foo'
                               , description='Description'
                               , meta_type='Foo'
                               , icon='foo.gif'
                               )
        self.assertEqual( ti.getId(), 'Foo' )
        self.assertEqual( ti.Title(), 'Foo' )
        self.assertEqual( ti.Description(), 'Description' )
        self.assertEqual( ti.Metatype(), 'Foo' )
        self.assertEqual( ti.getIcon(), 'foo.gif' )
        self.assertEqual( ti.immediate_view, '' )

        ti = self._makeInstance( 'Foo'
                               , immediate_view='foo_view'
                               )
        self.assertEqual( ti.immediate_view, 'foo_view' )

    def _makeAndSetInstance(self, id, **kw):
        tool = self.tool
        t = self._makeInstance(id, **kw)
        tool._setObject(id,t)
        return tool[id]

    def test_allowType( self ):
        self.tool = self._makeTypesTool()
        ti = self._makeAndSetInstance( 'Foo' )
        self.failIf( ti.allowType( 'Foo' ) )
        self.failIf( ti.allowType( 'Bar' ) )

        ti = self._makeAndSetInstance( 'Foo2', allowed_content_types=( 'Bar', ) )
        self.failUnless( ti.allowType( 'Bar' ) )

        ti = self._makeAndSetInstance( 'Foo3', filter_content_types=0 )
        self.failUnless( ti.allowType( 'Foo3' ) )

    def test_GlobalHide( self ):
        self.tool = self._makeTypesTool()
        tnf = self._makeAndSetInstance( 'Folder', filter_content_types=0)
        taf = self._makeAndSetInstance( 'Allowing Folder'
                                      , allowed_content_types=( 'Hidden'
                                                              ,'Not Hidden'))
        tih = self._makeAndSetInstance( 'Hidden', global_allow=0)
        tnh = self._makeAndSetInstance( 'Not Hidden')
        # make sure we're normally hidden but everything else is visible
        self.failIf     ( tnf.allowType( 'Hidden' ) )
        self.failUnless ( tnf.allowType( 'Not Hidden') )
        # make sure we're available where we should be
        self.failUnless ( taf.allowType( 'Hidden' ) )
        self.failUnless ( taf.allowType( 'Not Hidden') )
        # make sure we're available in a non-content-type-filtered type
        # where we have been explicitly allowed
        taf2 = self._makeAndSetInstance( 'Allowing Folder2'
                                       , allowed_content_types=( 'Hidden'
                                                               , 'Not Hidden'
                                                               )
                                       , filter_content_types=0
                                       )
        self.failUnless ( taf2.allowType( 'Hidden' ) )
        self.failUnless ( taf2.allowType( 'Not Hidden') )

    def test_allowDiscussion( self ):
        ti = self._makeInstance( 'Foo' )
        self.failIf( ti.allowDiscussion() )

        ti = self._makeInstance( 'Foo', allow_discussion=1 )
        self.failUnless( ti.allowDiscussion() )

    def test_listActions( self ):
        ti = self._makeInstance( 'Foo' )
        self.failIf( ti.listActions() )

        ti = self._makeInstance( **FTIDATA_ACTIONS[0] )
        actions = ti.listActions()
        self.failUnless( actions )

        ids = [ x.getId() for x in actions ]
        self.failUnless( 'view' in ids )
        self.failUnless( 'edit' in ids )
        self.failUnless( 'objectproperties' in ids )
        self.failUnless( 'slot' in ids )

        names = [ x.Title() for x in actions ]
        self.failUnless( 'View' in names )
        self.failUnless( 'Edit' in names )
        self.failUnless( 'Object Properties' in names )
        self.failIf( 'slot' in names )
        self.failUnless( 'Slot' in names )

        visible = [ x.getId() for x in actions if x.getVisibility() ]
        self.failUnless( 'view' in visible )
        self.failUnless( 'edit' in visible )
        self.failUnless( 'objectproperties' in visible )
        self.failIf( 'slot' in visible )

    def test_MethodAliases_methods(self):
        ti = self._makeInstance( **FTIDATA_CMF15[0] )
        self.assertEqual( ti.getMethodAliases(), FTIDATA_CMF15[0]['aliases'] )
        self.assertEqual( ti.queryMethodID('view'), 'dummy_view' )
        self.assertEqual( ti.queryMethodID('view.html'), 'dummy_view' )

        ti.setMethodAliases( ti.getMethodAliases() )
        self.assertEqual( ti.getMethodAliases(), FTIDATA_CMF15[0]['aliases'] )

    def _checkContentTI(self, ti):
        wanted_aliases = { 'view': 'dummy_view', '(Default)': 'dummy_view' }
        wanted_actions_text0 = 'string:${object_url}/dummy_view'
        wanted_actions_text1 = 'string:${object_url}/dummy_edit_form'
        wanted_actions_text2 = 'string:${object_url}/metadata_edit_form'

        self.failUnless( isinstance( ti._actions[0], ActionInformation ) )
        self.assertEqual( len( ti._actions ), 3 )
        self.assertEqual(ti._aliases, wanted_aliases)
        self.assertEqual(ti._actions[0].action.text, wanted_actions_text0)
        self.assertEqual(ti._actions[1].action.text, wanted_actions_text1)
        self.assertEqual(ti._actions[2].action.text, wanted_actions_text2)

        action0 = ti._actions[0]
        self.assertEqual( action0.getId(), 'view' )
        self.assertEqual( action0.Title(), 'View' )
        self.assertEqual( action0.getActionExpression(), wanted_actions_text0 )
        self.assertEqual( action0.getCondition(), '' )
        self.assertEqual( action0.getPermissions(), ( 'View', ) )
        self.assertEqual( action0.getCategory(), 'object' )
        self.assertEqual( action0.getVisibility(), 1 )

    def _checkFolderTI(self, ti):
        wanted_aliases = { 'view': '(Default)' }
        wanted_actions_text0 = 'string:${object_url}'
        wanted_actions_text1 = 'string:${object_url}/dummy_edit_form'
        wanted_actions_text2 = 'string:${object_url}/folder_localrole_form'

        self.failUnless( isinstance( ti._actions[0], ActionInformation ) )
        self.assertEqual( len( ti._actions ), 3 )
        self.assertEqual(ti._aliases, wanted_aliases)
        self.assertEqual(ti._actions[0].action.text, wanted_actions_text0)
        self.assertEqual(ti._actions[1].action.text, wanted_actions_text1)
        self.assertEqual(ti._actions[2].action.text, wanted_actions_text2)


class FTIDataTests( TypeInfoTests ):

    def _makeInstance(self, id, **kw):
        from Products.CMFCore.TypesTool import FactoryTypeInformation

        return FactoryTypeInformation(id, **kw)

    def test_z2interfaces(self):
        from Interface.Verify import verifyClass
        from Products.CMFCore.interfaces.portal_types \
                import ContentTypeInformation as ITypeInformation
        from Products.CMFCore.TypesTool import FactoryTypeInformation

        verifyClass(ITypeInformation, FactoryTypeInformation)

    def test_z3interfaces(self):
        from zope.interface.verify import verifyClass
        from Products.CMFCore.interfaces import ITypeInformation
        from Products.CMFCore.TypesTool import FactoryTypeInformation

        verifyClass(ITypeInformation, FactoryTypeInformation)

    def test_properties( self ):
        ti = self._makeInstance( 'Foo' )
        self.assertEqual( ti.product, '' )
        self.assertEqual( ti.factory, '' )

        ti = self._makeInstance( 'Foo'
                               , product='FooProduct'
                               , factory='addFoo'
                               )
        self.assertEqual( ti.product, 'FooProduct' )
        self.assertEqual( ti.factory, 'addFoo' )


class STIDataTests( TypeInfoTests ):

    def _makeInstance(self, id, **kw):
        from Products.CMFCore.TypesTool import ScriptableTypeInformation

        return ScriptableTypeInformation(id, **kw)

    def test_z2interfaces(self):
        from Interface.Verify import verifyClass
        from Products.CMFCore.interfaces.portal_types \
                import ContentTypeInformation as ITypeInformation
        from Products.CMFCore.TypesTool import ScriptableTypeInformation

        verifyClass(ITypeInformation, ScriptableTypeInformation)

    def test_z3interfaces(self):
        from zope.interface.verify import verifyClass
        from Products.CMFCore.interfaces import ITypeInformation
        from Products.CMFCore.TypesTool import ScriptableTypeInformation

        verifyClass(ITypeInformation, ScriptableTypeInformation)

    def test_properties( self ):
        ti = self._makeInstance( 'Foo' )
        self.assertEqual( ti.permission, '' )
        self.assertEqual( ti.constructor_path, '' )

        ti = self._makeInstance( 'Foo'
                               , permission='Add Foos'
                               , constructor_path='foo_add'
                               )
        self.assertEqual( ti.permission, 'Add Foos' )
        self.assertEqual( ti.constructor_path, 'foo_add' )


class FTIConstructionTests(unittest.TestCase):

    def setUp( self ):
        noSecurityManager()

    def _makeInstance(self, id, **kw):
        from Products.CMFCore.TypesTool import FactoryTypeInformation

        return FactoryTypeInformation(id, **kw)

    def _makeFolder( self, fake_product=0 ):
        return DummyFolder( fake_product )

    def test_isConstructionAllowed_wo_Container( self ):

        ti = self._makeInstance( 'foo' )

        self.failIf( ti.isConstructionAllowed( None ) )

        ti = self._makeInstance( 'Foo'
                               , product='FooProduct'
                               , factory='addFoo'
                               )

        self.failIf( ti.isConstructionAllowed( None ) )

    def test_isConstructionAllowed_wo_ProductFactory( self ):

        ti = self._makeInstance( 'foo' )

        folder = self._makeFolder()
        self.failIf( ti.isConstructionAllowed( folder ) )

        folder = self._makeFolder( fake_product=1 )
        self.failIf( ti.isConstructionAllowed( folder ) )

    def test_isConstructionAllowed_wo_Security( self ):

        ti = self._makeInstance( 'Foo'
                               , product='FooProduct'
                               , factory='addFoo'
                               )
        folder = self._makeFolder( fake_product=1 )

        self.failIf( ti.isConstructionAllowed( folder ) )


class FTIConstructionTests_w_Roles(unittest.TestCase):

    def tearDown( self ):
        noSecurityManager()

    def _makeStuff( self, prefix='' ):
        from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI

        ti = FTI( 'Foo'
                  , product='FooProduct'
                  , factory='addFoo'
                  )
        folder = DummyFolder( fake_product=1,prefix=prefix )

        return ti, folder

    def test_isConstructionAllowed_for_Omnipotent( self ):

        ti, folder = self._makeStuff()
        newSecurityManager( None
                          , OmnipotentUser().__of__( folder ) )
        self.failUnless( ti.isConstructionAllowed( folder ) )

    def test_isConstructionAllowed_w_Role( self ):

        ti, folder = self._makeStuff()

        newSecurityManager( None
                          , UserWithRoles( 'FooAdder' ).__of__( folder ) )
        self.failUnless( ti.isConstructionAllowed( folder ) )

    def test_isConstructionAllowed_wo_Role( self ):

        ti, folder = self._makeStuff()

        newSecurityManager( None
                          , UserWithRoles( 'FooViewer' ).__of__( folder ) )

    def test_constructInstance_wo_Roles( self ):

        ti, folder = self._makeStuff()

        newSecurityManager( None
                          , UserWithRoles( 'FooViewer' ).__of__( folder ) )

        self.assertRaises( Unauthorized
                         , ti.constructInstance, folder, 'foo' )

    def test_constructInstance( self ):

        ti, folder = self._makeStuff()

        newSecurityManager( None
                          , UserWithRoles( 'FooAdder' ).__of__( folder ) )

        ti.constructInstance( folder, 'foo' )
        foo = folder._getOb( 'foo' )
        self.assertEqual( foo.id, 'foo' )

    def test_constructInstance_private(self):
        ti, folder = self._makeStuff()
        newSecurityManager(None,
                           UserWithRoles('NotAFooAdder').__of__(folder))
        ti._constructInstance(folder, 'foo')
        foo = folder._getOb('foo')
        self.assertEqual(foo.id, 'foo')

    def test_constructInstance_w_args_kw( self ):

        ti, folder = self._makeStuff()

        newSecurityManager( None
                          , UserWithRoles( 'FooAdder' ).__of__( folder ) )

        ti.constructInstance( folder, 'bar', 0, 1 )
        bar = folder._getOb( 'bar' )
        self.assertEqual( bar.id, 'bar' )
        self.assertEqual( bar._args, ( 0, 1 ) )

        ti.constructInstance( folder, 'baz', frickle='natz' )
        baz = folder._getOb( 'baz' )
        self.assertEqual( baz.id, 'baz' )
        self.assertEqual( baz._kw[ 'frickle' ], 'natz' )

        ti.constructInstance( folder, 'bam', 0, 1, frickle='natz' )
        bam = folder._getOb( 'bam' )
        self.assertEqual( bam.id, 'bam' )
        self.assertEqual( bam._args, ( 0, 1 ) )
        self.assertEqual( bam._kw[ 'frickle' ], 'natz' )

    def test_constructInstance_w_id_munge( self ):

        ti, folder = self._makeStuff( 'majyk' )

        newSecurityManager( None
                          , UserWithRoles( 'FooAdder' ).__of__( folder ) )

        ti.constructInstance( folder, 'dust' )
        majyk_dust = folder._getOb( 'majyk_dust' )
        self.assertEqual( majyk_dust.id, 'majyk_dust' )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TypesToolTests),
        unittest.makeSuite(FTIDataTests),
        unittest.makeSuite(STIDataTests),
        unittest.makeSuite(FTIConstructionTests),
        unittest.makeSuite(FTIConstructionTests_w_Roles),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
