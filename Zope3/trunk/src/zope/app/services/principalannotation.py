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

"""Implementation of IPrincipalAnnotationService."""

# TODO: register service as adapter for IAnnotations on service activation
# this depends on existence of LocalAdapterService, so once that's done
# implement this.

# Zope3 imports
from persistence import Persistent
from persistence.dict import PersistentDict
from zodb.btrees.OOBTree import OOBTree
from zope.app.component.nextservice import queryNextService
from zope.context import ContextMethod
from zope.context import ContextWrapper
from zope.app.interfaces.annotation import IAnnotations

# Sibling imports
from zope.app.interfaces.services.principalannotation \
     import IPrincipalAnnotationService
from zope.app.interfaces.services.service import ISimpleService

class PrincipalAnnotationService(Persistent):
    """Stores IAnnotations for IPrinicipals.

    The service ID is 'PrincipalAnnotation'.
    """

    __implements__ = (IPrincipalAnnotationService, Persistent.__implements__,
                      ISimpleService)

    def __init__(self):
        self.annotations = OOBTree()


    # implementation of IPrincipalAnnotationService

    def getAnnotations(self, principal):
        """Return object implementing IAnnotations for the given principal.

        If there is no IAnnotations it will be created and then returned.
        """

        return self.getAnnotationsById(principal.getId())
            
    getAnnotations = ContextMethod(getAnnotations)

    def getAnnotationsById(self, principalId):
        """Return object implementing IAnnotations for the given principal.

        If there is no IAnnotations it will be created and then returned.
        """

        annotations = self.annotations.get(principalId)
        if annotations is None:
            annotations = Annotations(principalId, store=self.annotations)

        return ContextWrapper(annotations, self, name=principalId)
            
    getAnnotationsById = ContextMethod(getAnnotationsById)

    def hasAnnotations(self, principal):
        """Return boolean indicating if given principal has IAnnotations."""
        return principal.getId() in self.annotations


class Annotations(Persistent):
    """Stores annotations."""

    __implements__ = IAnnotations, Persistent.__implements__

    def __init__(self, principalId, store=None):
        self.principalId = principalId
        self.data = PersistentDict() # We don't really expect that many

        # _v_store is used to remember a mapping object that we should
        # be saved in if we ever change
        self._v_store = store

    def __getitem__(wrapped_self, key):
        try:
            return wrapped_self.data[key]
        except KeyError:
            # We failed locally: delegate to a higher-level service.
            service = queryNextService(wrapped_self, 'PrincipalAnnotation')
            if service is not None:
                annotations = service.getAnnotationsById(
                    wrapped_self.principalId)
                return annotations[key]
            raise

    __getitem__ = ContextMethod(__getitem__)

    def __setitem__(self, key, value):

        if getattr(self, '_v_store', None) is not None:
            # _v_store is used to remember a mapping object that we should
            # be saved in if we ever change
            self._v_store[self.principalId] = self
            del self._v_store

        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)


class AnnotationsForPrincipal(object):
    """Adapter from IPrincipal to IAnnotations for a PrincipalAnnotationService.

    Register an *instance* of this class as an adapter.
    """

    def __init__(self, service):
        self.service = service

    def __call__(self, principal):
        return self.service.getAnnotationsById(principal.getId())
