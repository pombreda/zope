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
"""This module tests the Gettext Export and Import funciotnality of the
Translation Service.

$Id: test_gettextexportimport.py,v 1.5 2003/02/11 15:59:58 sidnei Exp $
"""
import unittest, time

from cStringIO import StringIO

from zope.component.servicenames import Factories

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.component.metaconfigure import \
     provideService, managerHandler
from zope.app.component.metaconfigure import handler

from zope.app.services.translation.messagecatalog import \
     MessageCatalog
from zope.i18n.negotiator import negotiator
from zope.i18n.interfaces import INegotiator
from zope.i18n.interfaces import IUserPreferredLanguages

from zope.app.services.translation.translationservice import \
     TranslationService
from zope.app.services.translation.gettextimportfilter import \
     GettextImportFilter
from zope.app.services.translation.gettextexportfilter import \
     GettextExportFilter



class Environment:

    __implements__ = IUserPreferredLanguages

    def __init__(self, langs=()):
        self.langs = langs

    def getPreferredLanguages(self):
        return self.langs


class TestGettextExportImport(PlacelessSetup, unittest.TestCase):


    _data = '''msgid ""
msgstr ""
"Project-Id-Version: Zope 3\\n"
"PO-Revision-Date: %s\\n"
"Last-Translator: Zope 3 Gettext Export Filter\\n"
"Zope-Language: de\\n"
"Zope-Domain: default\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

msgid "Choose"
msgstr "Ausw\xc3\xa4hlen!"

msgid "greeting"
msgstr "hallo"
'''

    def setUp(self):
        PlacelessSetup.setUp(self)
        # Setup the negotiator service registry entry
        managerHandler('defineService', 'LanguageNegotiation', INegotiator)
        provideService('LanguageNegotiation', negotiator, 'zope.Public')
        self._service = TranslationService('default')
        handler(Factories, 'provideFactory', 'Message Catalog',
                MessageCatalog)


    def testImportExport(self):
        service = self._service

        imp = GettextImportFilter(service)
        imp.importMessages(['default'], ['de'],
                           StringIO(self._data %'2002/02/02 02:02'))

        exp = GettextExportFilter(service)
        result = exp.exportMessages(['default'], ['de'])

        dt = time.time()
        dt = time.localtime(dt)
        dt = time.strftime('%Y/%m/%d %H:%M', dt)

        self.assertEqual(result.strip(), (self._data %dt).strip())


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(TestGettextExportImport)


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
