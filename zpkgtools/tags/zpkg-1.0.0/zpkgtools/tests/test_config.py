##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests for zpkgtools.config."""

import os
import shutil
import tempfile
import unittest

from StringIO import StringIO

from zpkgsetup import cfgparser
from zpkgsetup import urlutils
from zpkgtools import config


here = os.path.dirname(os.path.abspath(__file__))


class ConfigTestCase(unittest.TestCase):

    def test_defaultConfigurationPath(self):
        # Not really sure what makes sense to check here, but at least
        # make sure it returns a string:
        path = config.defaultConfigurationPath()
        self.assert_(isinstance(path, basestring))

    def test_constructor(self):
        cf = config.Configuration()
        self.assert_(cf.include_support_code)
        self.assert_(not cf.application)
        self.assert_(not cf.collect_dependencies)
        self.assertEqual(len(cf.locations), 0)
        self.assertEqual(len(cf.location_maps), 0)
        self.assert_(not cf.default_collection)

    def test_loadPath(self):
        path = os.path.join(here, "zpkg-ok.conf")
        cf = config.Configuration()
        cf.loadPath(path)
        self.assertEqual(
            cf.location_maps,
            ["cvs://cvs.example.org/cvsroot:module/package/PACKAGES.txt",
             urlutils.file_url(os.path.join(here, "relative/path.txt"))])

    def test_constructor_bad_config_setting(self):
        # unknown option:
        self.assertRaises(cfgparser.ConfigurationError,
                          self.load_text, "unknown-option 42\n")

        # repository-map without path
        self.assertRaises(cfgparser.ConfigurationError,
                          self.load_text, "resource-map \n")

        # application too many times
        self.assertRaises(cfgparser.ConfigurationError,
                          self.load_text, ("build-application true\n"
                                           "build-application true\n"))

        # collect-dependencies too many times
        self.assertRaises(cfgparser.ConfigurationError,
                          self.load_text, ("collect-dependencies false\n"
                                           "collect-dependencies false\n"))

        # include-support-code too many times
        self.assertRaises(cfgparser.ConfigurationError,
                          self.load_text, ("include-support-code false\n"
                                           "include-support-code false\n"))

        # default-collection too many times
        self.assertRaises(cfgparser.ConfigurationError,
                          self.load_text, ("default-collection foo\n"
                                           "default-collection foo\n"))

        # default-collection with wildcard
        self.assertRaises(cfgparser.ConfigurationError,
                          self.load_text, "default-collection foo.*\n")

        # distribution-class too many times
        self.assertRaises(cfgparser.ConfigurationError,
                          self.load_text, ("distribution-class foo\n"
                                           "distribution-class foo\n"))

        # distribution-class with a bad value
        self.assertRaises(cfgparser.ConfigurationError,
                          self.load_text, "distribution-class not-really\n")

        # release-name too many times
        self.assertRaises(cfgparser.ConfigurationError,
                          self.load_text, ("release-name foo\n"
                                           "release-name foo\n"))

    def test_default_collection(self):
        cf = self.load_text("default-collection foo\n")
        self.assertEqual(cf.default_collection, "foo")

    def test_distribution_class(self):
        cf = self.load_text("distribution-class foo.bar\n")
        self.assertEqual(cf.distribution_class, "foo.bar")

    def test_release_name(self):
        cf = self.load_text("release-name foo\n")
        self.assertEqual(cf.release_name, "foo")

    def test_loadPath_no_such_file(self):
        path = os.path.join(here, "no-such-file")
        cf = config.Configuration()
        self.assertRaises(IOError, cf.loadPath, path)

    def test_simple_values_false(self):
        cf = self.load_text("build-application no\n"
                            "collect-dependencies false\n"
                            "include-support-code false\n")
        self.assert_(not cf.application)
        self.assert_(not cf.collect_dependencies)
        self.assert_(not cf.include_support_code)

    def test_simple_values_true(self):
        cf = self.load_text("build-application true\n"
                            "collect-dependencies yes\n"
                            "include-support-code true\n")
        self.assert_(cf.application)
        self.assert_(cf.collect_dependencies)
        self.assert_(cf.include_support_code)

    def test_embedded_resource_map(self):
        cf = config.Configuration()
        fd, path = tempfile.mkstemp(".conf", text=True)
        f = os.fdopen(fd, "w+")
        f.write(
            "<resources>\n"
            "  PKG1  svn://svn.example.net/repos/pkg1/trunk\n"
            "  pkg2  svn://svn.example.net/repos/proj/trunk/src/pkg2\n"
            "  rel  some/dir\n"
            "</resources>\n")
        f.close()
        where = os.path.dirname(path)
        whereurl = urlutils.file_url(where)
        try:
            cf.loadPath(path)
            self.assertEqual(cf.locations["PKG1"],
                             "svn://svn.example.net/repos/pkg1/trunk")
            self.assertEqual(cf.locations["pkg2"],
                             "svn://svn.example.net/repos/proj/trunk/src/pkg2")
            self.assertEqual(cf.locations["rel"],
                             whereurl + "/some/dir")
        finally:
            os.unlink(path)

    def test_nested_resources(self):
        self.assertRaises(
            cfgparser.ConfigurationError,
            self.load_text,
            "<resources>\n"
            "  PKG1  svn://svn.example.net/repos/pkg1/trunk\n"
            "  <resources>\n"
            "    pkg2  svn://svn.example.net/repos/proj/trunk/src/pkg2\n"
            "  </resources>\n"
            "</resources>\n")

    def test_embedded_resource_map_without_value(self):
        self.assertRaises(
            cfgparser.ConfigurationError,
            self.load_text,
            "<resources>\n"
            "  pkg  \n"
            "</resources>\n")

    def test_exclude_packages(self):
        cf = self.load_text(
            "<exclude>\n"
            "  reportlab\n"
            "  zope.app\n"
            "  zpkgsetup\n"
            "</exclude>\n")
        cf.exclude_packages.sort()
        self.assertEqual(cf.exclude_packages,
                         ['reportlab', 'zope.app', 'zpkgsetup'])

    def test_exclude_packages_does_not_allow_value(self):
        self.assertRaises(
            cfgparser.ConfigurationError,
            self.load_text,
            "<exclude>\n"
            "  reportlab   unnecessary junk\n"
            "</exclude>\n")

    def test_exclude_packages_does_not_allow_wildcard(self):
        self.assertRaises(
            cfgparser.ConfigurationError,
            self.load_text,
            "<exclude>\n"
            "  reportlab.*\n"
            "</exclude>\n")

    def test_support_packages(self):
        cf = self.load_text(
            "<support-packages>\n"
            "  some.package\n"
            "  another.package svn://svn.example.net/repo/somewhere/trunk\n"
            "</support-packages>\n")
        items = cf.support_packages.items()
        items.sort()
        self.assertEqual(
            items,
            [("another.package", "svn://svn.example.net/repo/somewhere/trunk"),
             ("some.package", None)])

    def test_support_packages_with_bad_key(self):
        self.assertRaises(
            cfgparser.ConfigurationError,
            self.load_text,
            "<support-packages>\n"
            "  foo-bar \n"
            "</support-packages>\n")

    def load_text(self, text, path=None, basedir=None):
        if path is None:
            if basedir is None:
                basedir = "foo"
            path = os.path.join(basedir, "bar.conf")
        if basedir is None:
            os.path.dirname(path)
        cf = config.Configuration()
        sio = StringIO(text)
        cf.loadStream(sio, path, basedir)
        return cf


class ConfigurationLocationMapIntegrationTestCase(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_relative_paths_mapped(self):
        os.mkdir(os.path.join(self.tmpdir, "releases"))
        reldir = os.path.join(self.tmpdir, "releases", "Thing")
        os.mkdir(reldir)
        cfgpath = os.path.join(reldir, "zpkg.conf")
        f = open(cfgpath, "w")
        f.write("resource-map one.map\n")
                #"resource-map two.map\n")
        f.close()
        mapfile = os.path.join(reldir, "one.map")
        f = open(mapfile, "w")
        f.write("pkg1 ../../src/pkg1\n"
                "pkg2 ../Thong\n"
                "pkg3 some/dir\n")
        f.close()

        cf = config.Configuration()
        old_path = os.getcwd()
        os.chdir(self.tmpdir)
        try:
            cf.loadPath("releases/Thing/zpkg.conf")
        finally:
            os.chdir(old_path)

        # make sure we're looking at the right location map:
        self.assertEqual(cf.location_maps, [urlutils.file_url(mapfile)])

        # load the finished map and make sure we get the right values:
        cf.finalize()
        expected = urlutils.file_url(
            os.path.join(self.tmpdir, "src", "pkg1"))
        self.assertEqual(cf.locations["pkg1"], expected)

        expected = urlutils.file_url(
            os.path.join(self.tmpdir, "releases", "Thong"))
        self.assertEqual(cf.locations["pkg2"], expected)

        expected = urlutils.file_url(
            os.path.join(self.tmpdir, "releases", "Thing", "some", "dir"))
        self.assertEqual(cf.locations["pkg3"], expected)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        unittest.makeSuite(ConfigTestCase))
    suite.addTest(
        unittest.makeSuite(ConfigurationLocationMapIntegrationTestCase))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
