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
$Id: i18nfile.py,v 1.3 2004/03/19 03:17:41 srichter Exp $
"""
from persistent import Persistent
from zope.interface import implements
from zope.publisher.browser import FileUpload
from zope.app.file.file import File

from interfaces import II18nFile

class I18nFile(Persistent):
    """I18n aware file object.  It contains a number of File objects --
    one for each language.
    """

    implements(II18nFile)

    def __init__(self, data='', contentType=None, defaultLanguage='en'):
        self._data = {}
        self.defaultLanguage = defaultLanguage
        self.setData(data, language=defaultLanguage)

        self.contentType = contentType or ''

    def _create(self, data):
        """Create a new subobject of the appropriate type.  Should be
        overriden in subclasses.
        """
        return File(data)

    def _get(self, language):
        """Helper function -- return a subobject for a given language,
        and if it does not exist, return a subobject for the default
        language.
        """
        file = self._data.get(language)
        if not file:
            file = self._data[self.defaultLanguage]
        return file

    def _get_or_add(self, language, data=''):
        """Helper function -- return a subobject for a given language,
        and if it does not exist, create and return a new subobject.
        """
        if language is None:
            language = self.defaultLanguage
        file = self._data.get(language)
        if not file:
            self._data[language] = file = self._create(data)
            self._p_changed = 1
        return file

    def getData(self, language=None):
        return self._get(language).data

    def setData(self, data, language=None):
        self._get_or_add(language).data = data

    # See IFile.
    data = property(getData, setData)

    def getSize(self, language=None):
        '''See interface IFile'''
        return self._get(language).getSize()

    def getDefaultLanguage(self):
        'See II18nAware'
        return self.defaultLanguage

    def setDefaultLanguage(self, language):
        'See II18nAware'
        if not self._data.has_key(language):
            raise ValueError, \
                  'cannot set nonexistent language (%s) as default' % language
        self.defaultLanguage = language

    def getAvailableLanguages(self):
        'See II18nAware'
        return self._data.keys()

    def removeLanguage(self, language):
        '''See interface II18nFile'''

        if language == self.defaultLanguage:
            raise ValueError, 'cannot remove default language (%s)' % language
        if self._data.has_key(language):
            del self._data[language]
            self._p_changed = True
