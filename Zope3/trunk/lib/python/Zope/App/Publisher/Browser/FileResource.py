##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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

$Id: FileResource.py,v 1.5 2002/07/13 18:00:12 jim Exp $
"""
__metaclass__ = type # All classes are new style when run with Python 2.2+

from Zope.Exceptions import NotFoundError

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.Publisher.Browser.IBrowserResource import IBrowserResource
from Zope.Publisher.Browser.IBrowserPublisher import IBrowserPublisher

from Zope.App.Publisher.FileResource import File, Image

from Zope.App.Publisher.Browser.Resource import Resource

class FileResource(BrowserView, Resource):

    __implements__ = IBrowserResource, IBrowserPublisher

    ############################################################
    # Implementation methods for interface
    # Zope.Publisher.Browser.IBrowserPublisher.

    def publishTraverse(self, request, name):
        '''See interface IBrowserPublisher'''
        raise NotFoundError(name)

    def browserDefault(self, request):
        '''See interface IBrowserPublisher'''
        method = request.get('REQUEST_METHOD', 'GET').upper()
        return getattr(self, method), ()

    #
    ############################################################

    # for unit tests
    def _testData(self):
        file = self.chooseContext()
        f=open(self.context.path,'rb')
        data=f.read()
        f.close()
        return data


    def chooseContext(self):
        """Choose the appropriate context"""
        return self.context


    def GET(self):
        """Default document"""

        file = self.chooseContext()
        request = self.request
        response = request.response

        # HTTP If-Modified-Since header handling. This is duplicated
        # from OFS.Image.Image - it really should be consolidated
        # somewhere...
        header = request.getHeader('If-Modified-Since', None)
        if header is not None:
            header = header.split(';')[0]
            # Some proxies seem to send invalid date strings for this
            # header. If the date string is not valid, we ignore it
            # rather than raise an error to be generally consistent
            # with common servers such as Apache (which can usually
            # understand the screwy date string as a lucky side effect
            # of the way they parse it).
            try:    mod_since=long(timeFromDateTimeString(header))
            except: mod_since=None
            if mod_since is not None:
                if getattr(file, 'lmt', None):
                    last_mod = long(file.lmt)
                else:
                    last_mod = long(0)
                if last_mod > 0 and last_mod <= mod_since:
                    response.setStatus(304)
                    return ''

        response.setHeader('Content-Type', file.content_type)
        response.setHeader('Last-Modified', file.lmh)

        # Cache for one day
        response.setHeader('Cache-Control', 'public,max-age=86400')
        f=open(file.path,'rb')
        data=f.read()
        f.close()
        
        return data

    def HEAD(self):
        file = self.chooseContext()
        response = self.request.response
        response = self.request.response
        response.setHeader('Content-Type', file.content_type)
        response.setHeader('Last-Modified', file.lmh)
        # Cache for one day
        response.setHeader('Cache-Control', 'public,max-age=86400')
        return ''
    

class FileResourceFactory:

    def __init__(self, path):
        self.__file = File(path)

    def __call__(self, request):
        return FileResource(self.__file, request)

class ImageResourceFactory:

    def __init__(self, path):
        self.__file = Image(path)

    def __call__(self, request):
        return FileResource(self.__file, request)
