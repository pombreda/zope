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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: test_ftpview.py,v 1.5 2003/11/27 13:59:20 philikon Exp $
"""

import datetime
from StringIO import StringIO
from unittest import TestCase, TestSuite, main, makeSuite
import zope.server.ftp.tests.demofs as demofs
from zope.app.interfaces.file import IReadFile, IWriteFile
from zope.app.interfaces.file import IReadDirectory, IWriteDirectory
from zope.app.interfaces.file import IFileFactory, IDirectoryFactory
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.ftp import FTPView
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.interface import implements
from zope.app.interfaces.copypastemove import IObjectMover
from zope.app.container.contained import setitem, Contained

class Directory(demofs.Directory, Contained):

    implements(IReadDirectory, IWriteDirectory, IFileFactory,
               IDirectoryFactory, IZopeDublinCore, IObjectMover)

    modified = datetime.datetime(1990, 1,1)

    def __setitem__(self, name, object):
        setitem(self, super(Directory, self).__setitem__, name, object)
        self.modified = datetime.datetime.now()

    def moveTo(self, target, new_name):
        source = self.__parent__
        old_name = self.__name__
        target[new_name] = self
        del source[old_name]

    def moveable(self):
        return True

    def moveableTo(self, target, name=None):
        return True
    
    def __call__(self, name, content_type='', data=None):
        if data:
            r = File()
            r.data = data
            return r
        return Directory()

class File(demofs.File):

    implements(IReadFile, IWriteFile, IZopeDublinCore)

    modified = datetime.datetime(1990, 1,2)

    def __init__(self, data=''):
        super(File, self).__init__()
        self.data = data

    def read(self):
        return self.data

    def size(self):
        return len(self.data)

    def write(self, data):
        self.data = data
        self.modified = datetime.datetime.now()

default_info = {
    'owner_name': 'na',
    'owner_readable': True,
    'owner_writable': True,
    'group_name': "na",
    'group_readable': True,
    'group_writable': True,
    'other_readable': False,
    'other_writable': False,
    'nlinks': 1,
    'size': 0,
    }

def norm_info(info):
    d = {}
    d.update(default_info)
    d.update(info)
    return d

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        super(Test, self).setUp()
        root = Directory()
        root['test'] = Directory()
        root['test2'] = Directory()
        root['f'] = File('contents of\nf')
        root['g'] = File('contents of\ng')
        self.__view = FTPView(root, None)

    def test_type(self):
        self.assertEqual(self.__view.type('test'), 'd')
        self.assertEqual(self.__view.type('f'), 'f')
        self.assertEqual(self.__view.type('missing'), None)

    def test_names(self):
        names = self.__view.names()
        names.sort()
        self.assertEqual(names, ['f', 'g', 'test', 'test2'])

    def test_ls(self):
        ls = map(norm_info, self.__view.ls())
        ls.sort(lambda i1, i2: cmp(i1['name'], i2['name']))
        self.assertEqual(
            ls,
            [{
            'name': 'f', 'type': 'f', 'size': 13,
            'mtime': datetime.datetime(1990, 1, 2),'nlinks': 1,
            'owner_name': 'na', 'owner_readable': 1, 'owner_writable': 1,
            'group_name': 'na', 'group_readable': 1, 'group_writable': 1,
            'other_readable': 0, 'other_writable': 0,
            },
             {
            'name': 'g', 'type': 'f', 'size': 13,
            'mtime': datetime.datetime(1990, 1, 2), 'nlinks': 1,
            'owner_name': 'na', 'owner_readable': 1, 'owner_writable': 1,
            'group_name': 'na', 'group_readable': 1, 'group_writable': 1,
            'other_writable': 0, 'other_readable': 0,
            }, {
            'name': 'test', 'type': 'd', 'size': 0,
            'mtime': datetime.datetime(1990, 1, 1), 'nlinks': 1,
            'owner_name': 'na', 'owner_readable': 1, 'owner_writable': 1,
            'group_name': 'na', 'group_readable': 1, 'group_writable': 1,
            'other_writable': 0, 'other_readable': 0,
            }, {
            'name': 'test2', 'type': 'd', 'size': 0,
            'mtime': datetime.datetime(1990, 1, 1), 'nlinks': 1,
            'owner_name': 'na', 'owner_readable': 1, 'owner_writable': 1,
            'group_name': 'na', 'group_readable': 1, 'group_writable': 1,
            'other_readable': 0, 'other_writable': 0,
            }])

    def test_readfile(self):
        f = StringIO()
        self.__view.readfile('f', f)
        self.assertEqual(f.getvalue(), 'contents of\nf')
        f = StringIO()
        self.__view.readfile('f', f, 3)
        self.assertEqual(f.getvalue(), 'tents of\nf')
        f = StringIO()
        self.__view.readfile('f', f, end=6)
        self.assertEqual(f.getvalue(), 'conten')
        f = StringIO()
        self.__view.readfile('f', f, 3, 9)
        self.assertEqual(f.getvalue(), 'contents of\nf'[3:9])

    def test_lsinfo(self):
        self.assertEqual(
            norm_info(self.__view.lsinfo('test')),
            {
            'name': 'test', 'type': 'd', 'size': 0,
            'mtime': datetime.datetime(1990, 1, 1), 'nlinks': 1,
            'owner_name': 'na', 'owner_readable': 1, 'owner_writable': 1,
            'group_name': 'na', 'group_readable': 1, 'group_writable': 1,
            'other_readable': 0, 'other_writable': 0,
            })
        self.assertEqual(
            norm_info(self.__view.lsinfo('f')),
            {
            'name': 'f', 'type': 'f', 'size': 13,
            'mtime': datetime.datetime(1990, 1, 2), 'nlinks': 1,
            'owner_name': 'na', 'owner_readable': 1, 'owner_writable': 1,
            'group_name': 'na', 'group_readable': 1, 'group_writable': 1,
            'other_readable': 0, 'other_writable': 0,
            })

    def test_mtime(self):
        self.assertEqual(self.__view.mtime('test'), Directory.modified)
        self.assertEqual(self.__view.mtime('f'), File.modified)

    def test_size(self):
        self.assertEqual(self.__view.size('test'), 0)
        self.assertEqual(self.__view.size('f'),
                         len(self.__view.context['f'].data))

    def test_mkdir(self):
        self.__view.mkdir('test3')
        names = self.__view.names()
        names.sort()
        self.assertEqual(names, ['f', 'g', 'test', 'test2', 'test3'])
        self.assertEqual(
            norm_info(self.__view.lsinfo('test3')),
            {
            'name': 'test3', 'type': 'd', 'size': 0,
            'mtime': datetime.datetime(1990, 1, 1), 'nlinks': 1,
            'owner_name': 'na', 'owner_readable': 1, 'owner_writable': 1,
            'group_name': 'na', 'group_readable': 1, 'group_writable': 1,
            'other_writable': 0, 'other_readable': 0,
            })

    def test_remove(self):
        self.__view.remove('g')
        names = self.__view.names()
        names.sort()
        self.assertEqual(names, ['f', 'test', 'test2'])

    def test_rmdir(self):
        self.__view.rmdir('test2')
        names = self.__view.names()
        names.sort()
        self.assertEqual(names, ['f', 'g', 'test'])

    def test_rename(self):
        self.__view.rename('test2', 'spam')
        names = self.__view.names()
        names.sort()
        self.assertEqual(names, ['f', 'g', 'spam', 'test'])

    def test_writefile_new(self):
        self.__view.writefile('foo', StringIO('foo contents'))
        self.assertEqual(self.__view.context['foo'].data, 'foo contents')

    def test_writefile_over(self):
        self.__view.writefile('f', StringIO('foo contents'))
        self.assertEqual(self.__view.context['f'].data, 'foo contents')
        self.__view.writefile('f', StringIO(' more'), append=True)
        self.assertEqual(self.__view.context['f'].data, 'foo contents more')
        self.__view.writefile('f', StringIO('xxxxxx'), start=3, end=9)
        self.assertEqual(self.__view.context['f'].data, 'fooxxxxxxnts more')
        self.__view.writefile('f', StringIO('yyy'), start=5)
        self.assertEqual(self.__view.context['f'].data, 'fooxxyyy')

    def test_writeable(self):
        self.assert_(self.__view.writable('f'))
        self.assert_(self.__view.writable('notthere'))
        self.assert_(not self.__view.writable('test'))

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
