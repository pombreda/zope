##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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

"""Test that the Zope schema can be loaded."""

import os
import cStringIO
import tempfile
import unittest

import ZConfig
import Zope.Startup

from Zope.Startup import datatypes

from App.config import getConfiguration


TEMPNAME = tempfile.mktemp()
TEMPPRODUCTS = os.path.join(TEMPNAME, "Products")


class StartupTestCase(unittest.TestCase):

    def load_config_text(self, text):
        # We have to create a directory of our own since the existence
        # of the directory is checked.  This handles this in a
        # platform-independent way.
        schema = Zope.Startup.getSchema()
        sio = cStringIO.StringIO(
            text.replace("<<INSTANCE_HOME>>", TEMPNAME))
        os.mkdir(TEMPNAME)
        os.mkdir(TEMPPRODUCTS)
        try:
            conf, handler = ZConfig.loadConfigFile(schema, sio)
        finally:
            os.rmdir(TEMPPRODUCTS)
            os.rmdir(TEMPNAME)
        self.assertEqual(conf.instancehome, TEMPNAME)
        return conf

    def test_load_config_template(self):
        schema = Zope.Startup.getSchema()
        cfg = getConfiguration()
        fn = os.path.join(cfg.zopehome, "skel", "etc", "zope.conf.in")
        f = open(fn)
        text = f.read()
        f.close()
        self.load_config_text(text)

    def test_cgi_environment(self):
        conf = self.load_config_text("""\
            # instancehome is here since it's required
            instancehome <<INSTANCE_HOME>>
            <cgi-environment>
              HEADER value
              ANOTHER value2
            </cgi-environment>
            """)
        items = conf.cgi_environment.items()
        items.sort()
        self.assertEqual(items, [("ANOTHER", "value2"), ("HEADER", "value")])

    def test_access_and_trace_logs(self):
        fn = tempfile.mktemp()
        conf = self.load_config_text("""
            instancehome <<INSTANCE_HOME>>
            <logger access>
              <logfile>
                path %s
              </logfile>
            </logger>
            """ % fn)
        self.assert_(isinstance(conf.access, datatypes.LoggerFactory))
        self.assertEqual(conf.access.name, "access")
        self.assertEqual(conf.access.handler_factories[0].section.path, fn)
        self.assert_(conf.trace is None)

    def test_dns_resolver(self):
        from ZServer.medusa import resolver
        conf = self.load_config_text("""\
            instancehome <<INSTANCE_HOME>>
            dns-server localhost
            """)
        self.assert_(isinstance(conf.dns_resolver, resolver.caching_resolver))


def test_suite():
    return unittest.makeSuite(StartupTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
