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
$Id: test_baserequest.py,v 1.2 2002/12/25 14:15:19 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.testing.cleanup import CleanUp # Base class w registry cleanup

from zope.publisher.tests.basetestipublicationrequest \
     import BaseTestIPublicationRequest

from zope.publisher.tests.basetestipublisherrequest \
     import BaseTestIPublisherRequest

from zope.publisher.tests.basetestiapplicationrequest \
     import BaseTestIApplicationRequest

from StringIO import StringIO

class TestBaseRequest(BaseTestIPublicationRequest,
                      BaseTestIApplicationRequest,
                      BaseTestIPublisherRequest,
                      TestCase):

    def _Test__new(self, **kw):
        from zope.publisher.base import BaseRequest
        return BaseRequest(StringIO(''), StringIO(), kw)

    def _Test__expectedViewType(self):
        return None # we don't expect

    def test_IApplicationRequest_body(self):
        from zope.publisher.base import BaseRequest

        request = BaseRequest(StringIO('spam'), StringIO(), {})
        self.assertEqual(request.body, 'spam')

        request = BaseRequest(StringIO('spam'), StringIO(), {})
        self.assertEqual(request.bodyFile.read(), 'spam')

    def test_IPublicationRequest_getPositionalArguments(self):
        self.assertEqual(self._Test__new().getPositionalArguments(), ())

    def test_IPublisherRequest_retry(self):
        self.assertEqual(self._Test__new().supportsRetry(), 0)

    def test_IPublisherRequest_traverse(self):
        from zope.publisher.tests.publication import TestPublication
        request = self._Test__new()
        request.setPublication(TestPublication())
        app = request.publication.getApplication(request)

        request.setTraversalStack([])
        self.assertEqual(request.traverse(app).name, '')
        request.setTraversalStack(['ZopeCorp'])
        self.assertEqual(request.traverse(app).name, 'ZopeCorp')
        request.setTraversalStack(['Engineering', 'ZopeCorp'])
        self.assertEqual(request.traverse(app).name, 'Engineering')

    def test_IPublisherRequest_processInputs(self):
        self._Test__new().processInputs()


    # Needed by BaseTestIEnumerableMapping tests:
    def _IEnumerableMapping__stateDict(self):
        return {'id': 'ZopeOrg', 'title': 'Zope Community Web Site',
                'greet': 'Welcome to the Zope Community Web site'}

    def _IEnumerableMapping__sample(self):
        return self._Test__new(**(self._IEnumerableMapping__stateDict()))

    def _IEnumerableMapping__absentKeys(self):
        return 'foo', 'bar'


def test_suite():
    return makeSuite(TestBaseRequest)

if __name__=='__main__':
    main(defaultTest='test_suite')
