import os, sys
import unittest
import time
from cStringIO import StringIO

from OFS.Application import Application
from OFS.SimpleItem import SimpleItem
from OFS.Cache import ZCM_MANAGERS
from OFS.Image import Pdata
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from App.Common import rfc1123_date
from Testing.makerequest import makerequest
from zExceptions import Redirect

try:
    here = os.path.dirname(os.path.abspath(__file__))
except:
    here = os.path.dirname(os.path.abspath(sys.argv[0]))

imagedata = os.path.join(here, 'test.gif')
filedata = os.path.join(here, 'test.gif')

def makeConnection():
    import ZODB
    from ZODB.DemoStorage import DemoStorage

    s = DemoStorage(quota=(1<<20))
    return ZODB.DB( s ).open()


def aputrequest(file, content_type):
    resp = HTTPResponse(stdout=sys.stdout)
    environ = {}
    environ['SERVER_NAME']='foo'
    environ['SERVER_PORT']='80'
    environ['REQUEST_METHOD'] = 'PUT'
    environ['CONTENT_TYPE'] = content_type
    req = HTTPRequest(stdin=file, environ=environ, response=resp)
    return req

class DummyCache:
    def __init__(self):
        self.clear()
        
    def ZCache_set(self, ob, data, view_name='', keywords=None,
                   mtime_func=None):
        self.set = (ob, data)
    
    def ZCache_get(self, ob, data, view_name='', keywords=None,
                   mtime_func=None):
        self.get = ob
        if self.si:
            return si

    def ZCache_invalidate(self, ob):
        self.invalidated = ob

    def clear(self):
        self.set=None
        self.get=None
        self.invalidated = None
        self.si = None

    def setStreamIterator(self, si):
        self.si = si
    

ADummyCache=DummyCache()

class DummyCacheManager(SimpleItem):
    def ZCacheManager_getCache(self):
        return ADummyCache
    
class FileTests(unittest.TestCase):
    data = open(filedata, 'rb').read()
    content_type = 'application/octet-stream'
    factory = 'manage_addFile'
    def setUp( self ):

        self.connection = makeConnection()
        try:
            r = self.connection.root()
            a = Application()
            r['Application'] = a
            self.root = a
            responseOut = self.responseOut = StringIO()
            self.app = makerequest( self.root, stdout=responseOut )
            self.app.dcm = DummyCacheManager()
            factory = getattr(self.app, self.factory)
            factory('file',
                    file=self.data, content_type=self.content_type)
            self.app.file.ZCacheable_setManagerId('dcm')
            self.app.file.ZCacheable_setEnabled(enabled=1)
            setattr(self.app, ZCM_MANAGERS, ('dcm',))
            # Hack, we need a _p_mtime for the file, so we make sure that it
            # has one.
            get_transaction().commit()
        except:
            self.connection.close()
            raise
        get_transaction().begin()
        self.file = getattr( self.app, 'file' )

    def tearDown( self ):
        del self.file
        get_transaction().abort()
        self.connection.close()
        del self.app
        del self.responseOut
        del self.root
        del self.connection
        ADummyCache.clear()

    def testViewImageOrFile(self):
        self.assertRaises(Redirect, self.file.view_image_or_file, 'foo')

    def testUpdateData(self):
        self.file.update_data('foo')
        self.assertEqual(self.file.size, 3)
        self.assertEqual(self.file.data, 'foo')
        self.failUnless(ADummyCache.invalidated)
        self.failUnless(ADummyCache.set)

    def testReadData(self):
        s = "a" * (2 << 16)
        f = StringIO(s)
        data, size = self.file._read_data(f)
        self.failUnless(isinstance(data, Pdata))
        self.assertEqual(str(data), s)
        self.assertEqual(len(s), len(str(data)))
        self.assertEqual(len(s), size)

    def testManageEditWithFileData(self):
        self.file.manage_edit('foobar', 'text/plain', filedata='ASD')
        self.assertEqual(self.file.title, 'foobar')
        self.assertEqual(self.file.content_type, 'text/plain')
        self.failUnless(ADummyCache.invalidated)
        self.failUnless(ADummyCache.set)
        
    def testManageEditWithoutFileData(self):
        self.file.manage_edit('foobar', 'text/plain')
        self.assertEqual(self.file.title, 'foobar')
        self.assertEqual(self.file.content_type, 'text/plain')
        self.failUnless(ADummyCache.invalidated)

    def testManageUpload(self):
        f = StringIO('jammyjohnson')
        self.file.manage_upload(f)
        self.assertEqual(self.file.data, 'jammyjohnson')
        self.assertEqual(self.file.content_type, 'application/octet-stream')

    def testIfModSince(self):
        now = time.time()
        e = {'SERVER_NAME':'foo', 'SERVER_PORT':'80', 'REQUEST_METHOD':'GET'}

        # not modified since
        t_notmod = rfc1123_date(now)
        e['HTTP_IF_MODIFIED_SINCE'] = t_notmod
        out = StringIO()
        resp = HTTPResponse(stdout=out)
        req = HTTPRequest(sys.stdin, e, resp)
        data = self.file.index_html(req,resp)
        self.assertEqual(resp.getStatus(), 304)
        self.assertEqual(data, '')

        # modified since
        t_mod = rfc1123_date(now - 100)
        e['HTTP_IF_MODIFIED_SINCE'] = t_mod
        out = StringIO()
        resp = HTTPResponse(stdout=out)
        req = HTTPRequest(sys.stdin, e, resp)
        data = self.file.index_html(req,resp)
        self.assertEqual(resp.getStatus(), 200)
        self.assertEqual(data, str(self.file.data))

    def testPUT(self):
        s = '# some python\n'

        # with content type
        data = StringIO(s)
        req = aputrequest(data, 'text/x-python')
        req.processInputs()
        self.file.PUT(req, req.RESPONSE)

        self.assertEqual(self.file.content_type, 'text/x-python')
        self.assertEqual(str(self.file.data), s)

        # without content type
        data.seek(0)
        req = aputrequest(data, '')
        req.processInputs()
        self.file.PUT(req, req.RESPONSE)

        self.assertEqual(self.file.content_type, 'text/x-python')
        self.assertEqual(str(self.file.data), s)

    def testIndexHtmlWithPdata(self):
        self.file.manage_upload('a' * (2 << 16)) # 128K
        self.file.index_html(self.app.REQUEST, self.app.REQUEST.RESPONSE)
        self.assert_(self.app.REQUEST.RESPONSE._wrote)

    def testIndexHtmlWithString(self):
        self.file.manage_upload('a' * 100) # 100 bytes
        self.file.index_html(self.app.REQUEST, self.app.REQUEST.RESPONSE)
        self.assert_(not self.app.REQUEST.RESPONSE._wrote)

    def testStr(self):
        self.assertEqual(str(self.file), self.data)

class ImageTests(FileTests):
    data = open(filedata, 'rb').read()
    content_type = 'image/gif'
    factory = 'manage_addImage'

    def testUpdateData(self):
        self.file.update_data(self.data)
        self.assertEqual(self.file.size, len(self.data))
        self.assertEqual(self.file.data, self.data)
        self.assertEqual(self.file.width, 16)
        self.assertEqual(self.file.height, 16)
        self.failUnless(ADummyCache.invalidated)
        self.failUnless(ADummyCache.set)
        
    def testStr(self):
        self.assertEqual(str(self.file),
          ('<img src="http://foo/file" alt="" title="" height="16" width="16" '
           'border="0" />'))

    def testTag(self):
        self.assertEqual(self.file.tag(),
          ('<img src="http://foo/file" alt="" title="" height="16" width="16" '
           'border="0" />'))

    def testViewImageOrFile(self):
        pass # dtml method,screw it
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( FileTests ) )
    suite.addTest( unittest.makeSuite( ImageTests ))
    return suite

if __name__ == "__main__":
    unittest.main()
