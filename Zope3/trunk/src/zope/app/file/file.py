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
"""File content component

$Id: file.py,v 1.3 2004/03/02 14:40:02 philikon Exp $
"""
from persistent import Persistent
from transaction import get_transaction
from zope.interface import implements

from zope.publisher.browser import FileUpload
from interfaces import IFile, IReadFile, IFileContent

__metaclass__ = type

# set the size of the chunks
MAXCHUNKSIZE = 1 << 16

class File(Persistent):
    """A persistent content component storing binary file data

    Let's test the constructor:

    >>> file = File()
    >>> file.getContentType()
    ''
    >>> file.getData()
    ''

    >>> file = File('Foobar')
    >>> file.getContentType()
    ''
    >>> file.getData()
    'Foobar'

    >>> file = File('Foobar', 'text/plain')
    >>> file.getContentType()
    'text/plain'
    >>> file.getData()
    'Foobar'

    >>> file = File(data='Foobar', contentType='text/plain')
    >>> file.getContentType()
    'text/plain'
    >>> file.getData()
    'Foobar'


    Let's test the mutators:

    >>> file = File()
    >>> file.setContentType('text/plain')
    >>> file.getContentType()
    'text/plain'

    >>> file.setData('Foobar')
    >>> file.getData()
    'Foobar'

    >>> file.edit('Blah', 'text/html')
    >>> file.getContentType()
    'text/html'
    >>> file.getData()
    'Blah'

    >>> file.setData(None)
    Traceback (most recent call last):
    ...
    TypeError: Cannot set None data on a file.


    Let's test large data input:

    >>> file = File()

    Insert as string:

    >>> file.setData('Foobar'*60000)
    >>> file.getSize()
    360000
    >>> file.getData() == 'Foobar'*60000
    True

    Insert data as FileChunk:

    >>> fc = FileChunk('Foobar'*4000)
    >>> file.setData(fc)
    >>> file.getSize()
    24000
    >>> file.getData() == 'Foobar'*4000
    True

    Insert data from file object:

    >>> import cStringIO
    >>> sio = cStringIO.StringIO()
    >>> sio.write('Foobar'*100000)
    >>> sio.seek(0)
    >>> file.setData(sio)
    >>> file.getSize()
    600000
    >>> file.getData() == 'Foobar'*100000
    True


    Last, but not least, verify the interface:

    >>> from zope.interface.verify import verifyClass
    >>> IFile.isImplementedByInstancesOf(File)
    True
    >>> verifyClass(IFile, File)
    True
    """
    
    implements(IFileContent, IFile)

    def __init__(self, data='', contentType=''):
        self.data = data
        self.contentType = contentType

    def __len__(self):
        return self.size

    def setContentType(self, contentType):
        '''See interface IFile'''
        self._contentType = contentType

    def getContentType(self):
        '''See interface IFile'''
        return self._contentType

    def edit(self, data, contentType=None):
        '''See interface IFile'''
        # XXX This seems broken to me, as setData can override the
        # content type explicitly passed in.

        if contentType is not None:
            self._contentType = contentType
        if isinstance(data, FileUpload) and not data.filename:
            data = None          # Ignore empty files
        if data is not None:
            self.data = data

    def getData(self):
        '''See interface IFile'''
        if isinstance(self._data, FileChunk):
            return str(self._data)
        else:
            return self._data

    def setData(self, data):
        '''See interface IFile'''
        # Handle case when data is a string
        if isinstance(data, unicode):
            data = data.encode('UTF-8')

        if isinstance(data, str):
            self._data, self._size = FileChunk(data), len(data)
            return

        # Handle case when data is None
        if data is None:
            raise TypeError('Cannot set None data on a file.')

        # Handle case when data is already a FileChunk
        if isinstance(data, FileChunk):
            size = len(data)
            self._data, self._size = data, size
            return

        # Handle case when data is a file object
        seek = data.seek
        read = data.read

        seek(0, 2)
        size = end = data.tell()

        if size <= 2*MAXCHUNKSIZE:
            seek(0)
            if size < MAXCHUNKSIZE:
                self._data, self._size = read(size), size
                return
            self._data, self._size = FileChunk(read(size)), size
            return

        # Make sure we have an _p_jar, even if we are a new object, by
        # doing a sub-transaction commit.
        get_transaction().commit(1)

        jar = self._p_jar

        if jar is None:
            # Ugh
            seek(0)
            self._data, self._size = FileChunk(read(size)), size
            return

        # Now we're going to build a linked list from back
        # to front to minimize the number of database updates
        # and to allow us to get things out of memory as soon as
        # possible.
        next = None
        while end > 0:
            pos = end - MAXCHUNKSIZE
            if pos < MAXCHUNKSIZE:
                pos = 0 # we always want at least MAXCHUNKSIZE bytes
            seek(pos)
            data = FileChunk(read(end - pos))

            # Woooop Woooop Woooop! This is a trick.
            # We stuff the data directly into our jar to reduce the
            # number of updates necessary.
            data._p_jar = jar

            # This is needed and has side benefit of getting
            # the thing registered:
            data.next = next

            # Now make it get saved in a sub-transaction!
            get_transaction().savepoint()

            # Now make it a ghost to free the memory.  We
            # don't need it anymore!
            data._p_changed = None

            next = data
            end = pos

        self._data, self._size = next, size
        return

    def getSize(self):
        '''See interface IFile'''
        return self._size

    data = property(getData, setData, None,
                    """Contains the data of the file.""")

    contentType = property(getContentType, setContentType, None,
                           """Specifies the content type of the data.""")

    size = property(getSize, None, None,
                    """Specifies the size of the file in bytes. Read only.""")


# Adapter for ISearchableText

from zope.app.index.interfaces.text import ISearchableText

class SearchableText:

    implements(ISearchableText)
    __used_for__ = IReadFile

    def __init__(self, file):
        self.file = file

    def getSearchableText(self):
        if self.file.contentType == "text/plain":
            return [unicode(self.file.data)]
        else:
            return None


class FileChunk(Persistent):
    # Wrapper for possibly large data

    next = None

    def __init__(self, data):
        self._data = data

    def __getslice__(self, i, j):
        return self._data[i:j]

    def __len__(self):
        data = str(self)
        return len(data)

    def __str__(self):
        next = self.next
        if next is None:
            return self._data

        result = [self._data]
        while next is not None:
            self = next
            result.append(self._data)
            next = self.next

        return ''.join(result)

class FileReadFile:
    """Adapter for file-system style read access.

    >>> file = File()
    >>> content = "This is some file\\ncontent."
    >>> file.edit(content, 'text/plain')
    >>> FileReadFile(file).read() == content
    True
    >>> FileReadFile(file).size() == len(content)
    True
    """

    def __init__(self, context):
        self.context = context

    def read(self):
        return self.context.getData()

    def size(self):
        return len(self.context.getData())

class FileWriteFile:
    """Adapter for file-system style write access.

    >>> file = File()
    >>> content = "This is some file\\ncontent."
    >>> FileWriteFile(file).write(content)
    >>> file.getData() == content
    True
    """

    def __init__(self, context):
        self.context = context

    def write(self, data):
        self.context.setData(data)
