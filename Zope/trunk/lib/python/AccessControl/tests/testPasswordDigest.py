##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
"""Test of AuthEncoding
"""

__rcs_id__='$Id: testPasswordDigest.py,v 1.2 2001/10/17 20:00:32 tseaver Exp $'
__version__='$Revision: 1.2 $'[11:-2]

import os, sys, unittest

from AccessControl import AuthEncoding
import unittest


class PasswordDigestTests (unittest.TestCase):

    def testGoodPassword(self):
        pw = 'good_password'
        assert len(AuthEncoding.listSchemes()) > 0  # At least one must exist!
        for id in AuthEncoding.listSchemes():
            enc = AuthEncoding.pw_encrypt(pw, id)
            assert enc != pw
            assert AuthEncoding.pw_validate(enc, pw)
            assert AuthEncoding.is_encrypted(enc)
            assert not AuthEncoding.is_encrypted(pw)

    def testBadPasword(self):
        pw = 'OK_pa55w0rd \n'
        for id in AuthEncoding.listSchemes():
            enc = AuthEncoding.pw_encrypt(pw, id)
            assert enc != pw
            assert not AuthEncoding.pw_validate(enc, 'xxx')
            assert not AuthEncoding.pw_validate(enc, enc)
            if id != 'CRYPT':
                # crypt truncates passwords and would fail this test.
                assert not AuthEncoding.pw_validate(enc, pw[:-1])
            assert not AuthEncoding.pw_validate(enc, pw[1:])
            assert AuthEncoding.pw_validate(enc, pw)

    def testShortPassword(self):
        pw = '1'
        for id in AuthEncoding.listSchemes():
            enc = AuthEncoding.pw_encrypt(pw, id)
            assert enc != pw
            assert AuthEncoding.pw_validate(enc, pw)
            assert not AuthEncoding.pw_validate(enc, enc)
            assert not AuthEncoding.pw_validate(enc, 'xxx')

    def testLongPassword(self):
        pw = 'Pw' * 10000
        for id in AuthEncoding.listSchemes():
            enc = AuthEncoding.pw_encrypt(pw, id)
            assert enc != pw
            assert AuthEncoding.pw_validate(enc, pw)
            assert not AuthEncoding.pw_validate(enc, enc)
            assert not AuthEncoding.pw_validate(enc, 'xxx')
            if id != 'CRYPT':
                # crypt truncates passwords and would fail these tests.
                assert not AuthEncoding.pw_validate(enc, pw[:-2])
                assert not AuthEncoding.pw_validate(enc, pw[2:])
            
    def testBlankPassword(self):
        pw = ''
        for id in AuthEncoding.listSchemes():
            enc = AuthEncoding.pw_encrypt(pw, id)
            assert enc != pw
            assert AuthEncoding.pw_validate(enc, pw)
            assert not AuthEncoding.pw_validate(enc, enc)
            assert not AuthEncoding.pw_validate(enc, 'xxx')

    def testUnencryptedPassword(self):
        # Sanity check
        pw = 'my-password'
        assert AuthEncoding.pw_validate(pw, pw)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( PasswordDigestTests ) )
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
