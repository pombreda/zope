# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 1.2.10.3.8.1 $
# Date: $Date: 2004/05/12 19:57:42 $
# Copyright: This module has been placed in the public domain.

# Internationalization details are documented in
# <http://docutils.sf.net/spec/howto/i18n.html>.

"""
This package contains modules for language-dependent features of Docutils.
"""

__docformat__ = 'reStructuredText'

_languages = {}

def get_language(language_code):
    if _languages.has_key(language_code):
        return _languages[language_code]
    module = __import__(language_code, globals(), locals())
    _languages[language_code] = module
    return module
