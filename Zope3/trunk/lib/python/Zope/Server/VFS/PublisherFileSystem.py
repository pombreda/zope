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

$Id: PublisherFileSystem.py,v 1.3 2002/06/18 14:47:08 jim Exp $
"""

import re
import stat
import time
import posixpath

from cStringIO import StringIO

from IReadFileSystem import IReadFileSystem
from IWriteFileSystem import IWriteFileSystem

from Zope.Publisher.Publish import publish



class NoOutput:
    """An output stream lookalike that warns you if you try to
    dump anything into it."""

    def write(self, data):
        raise RuntimeError, "Not a writable stream"

    def flush(self):
        pass

    close = flush



class PublisherFileSystem:
    """Generic Publisher FileSystem implementation.
    """

    __implements__ = IReadFileSystem, IWriteFileSystem

    def __init__ (self, credentials, request_factory):
        self.credentials = credentials
        self.request_factory = request_factory


    def _execute(self, path, command, env=None):
        if env is None:
            env = {}

        env['command'] = command
        env['path'] = path
        env['credentials'] = self.credentials
        # NoOutput avoids creating a black hole.
        request = self.request_factory(StringIO(''), NoOutput(), env)
        # Note that publish() calls close() on request, which deletes the
        # response from the request, so that we need to keep track of it.
        response = request.response
        publish(request)
        return response.getResult()


    ############################################################
    # Implementation methods for interface
    # Zope.Server.VFS.IReadFileSystem.

    def exists(self, path):
        'See Zope.Server.VFS.IReadFileSystem.IReadFileSystem'
        path = self.translate(path)
        if path == '/':
            return 1
        path, file = posixpath.split(path)
        env = {'name': file}
        return self._execute(path, 'exists', env)


    def isdir(self, path):
        'See Zope.Server.VFS.IReadFileSystem.IReadFileSystem'
        path = self.translate(path)
        return self._execute(path, 'isdir')


    def isfile(self, path):
        'See Zope.Server.VFS.IReadFileSystem.IReadFileSystem'
        path = self.translate(path)
        return self._execute(path, 'isfile')


    def listdir(self, path, with_stats=0, pattern='*'):
        'See Zope.Server.VFS.IReadFileSystem.IReadFileSystem'
        path = self.translate(path)
        env = {'with_stats' : with_stats,
               'pattern' : pattern}
        return self._execute(path, 'listdir', env)


    def readfile(self, path, mode, outstream, start=0, end=-1):
        'See Zope.Server.VFS.IReadFileSystem.IReadFileSystem'
        path = self.translate(path)
        env = {'mode'      : mode,
               'outstream' : outstream,
               'start'     : start,
               'end'       : end}
        return self._execute(path, 'read', env)


    def stat(self, path):
        'See Zope.Server.VFS.IReadFileSystem.IReadFileSystem'
        path = self.translate(path)
        return self._execute(path, 'stat')

    #
    ############################################################

    ############################################################
    # Implementation methods for interface
    # Zope.Server.VFS.IWriteFileSystem.

    def mkdir(self, path, mode=777):
        'See Zope.Server.VFS.IWriteFileSystem.IWriteFileSystem'
        path = self.translate(path)
        path, dir = posixpath.split(path)
        env = {'name': dir}
        return self._execute(path, 'mkdir', env)


    def remove(self, path):
        'See Zope.Server.VFS.IWriteFileSystem.IWriteFileSystem'
        path = self.translate(path)
        path, name = posixpath.split(path)
        env = {'name': name}
        return self._execute(path, 'remove', env)


    def rmdir(self, path):
        'See Zope.Server.VFS.IWriteFileSystem.IWriteFileSystem'
        path = self.translate(path)
        path, dir = posixpath.split(path)
        env = {'name': dir}
        return self._execute(path, 'rmdir', env)


    def rename(self, old, new):
        'See Zope.Server.VFS.IWriteFileSystem.IWriteFileSystem'
        old = self.translate(old)
        new = self.translate(new)
        path0, old = posixpath.split(old)
        path1, new = posixpath.split(new)
        assert path0 == path1
        env = {'old' : old,
               'new' : new}
        return self._execute(path0, 'rename', env)

    def writefile(self, path, mode, instream, start=0):
        'See Zope.Server.VFS.IWriteFileSystem.IWriteFileSystem'
        path = self.translate(path)
        path, name = posixpath.split(path)
        env = {'name'      : name,
               'mode'      : mode,
               'instream'  : instream,
               'start'     : start}
        return self._execute(path, 'writefile', env)


    def check_writable(self, path):
        'See Zope.Server.VFS.IWriteFileSystem.IWriteFileSystem'
        path = self.translate(path)
        path, name = posixpath.split(path)
        env = {'name'      : name}
        return self._execute(path, 'check_writable', env)

    #
    ############################################################

    # utility methods

    def translate (self, path):
        # Normalize
        path = posixpath.normpath(path)
        if path.startswith('..'):
            # Someone is trying to get lower than the permitted root.
            # We just ignore it.
            path = '/'
        return path

