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
import unittest

# Note: The expected output is in order of preference,
# empty 'q=' means 'q=1', and if theres more than one
# empty, we assume they are in order of preference.
data = [
    ('da, en, pt', ['da', 'en', 'pt']),
    ('da, en;q=.9, en-gb;q=1.0, en-us', ['da', 'en-gb', 'en-us', 'en']),
    ('pt_BR; q=0.6, pt_PT; q = .7, en-gb', ['en-gb', 'pt-pt', 'pt-br']),
    ('en-us, en_GB;q=0.9, en, pt_BR; q=1.0', ['en-us', 'en', 'pt-br', 'en-gb']),
    ('ro,en-us;q=0.8,es;q=0.5,fr;q=0.3', ['ro', 'en-us', 'es', 'fr']),
    ('ro,en-us;q=0,es;q=0.5,fr;q=0,ru;q=1,it', ['ro', 'ru', 'it', 'es'])
    ]


class BrowserLanguagesTest(unittest.TestCase):

    def test_browser_language_handling(self):
        from zope.publisher.browser import BrowserLanguages
        for req, expected in data:
            request = {'HTTP_ACCEPT_LANGUAGE': req}
            browser_languages = BrowserLanguages(request)
            self.assertEqual(list(browser_languages.getPreferredLanguages()),
                             expected)

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(BrowserLanguagesTest)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
