##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Generator for distutils setup.py files."""

import logging
import os
import posixpath
import sys

from zpkgtools import package
from zpkgtools import publication


_logger = logging.getLogger(__name__)


class SetupContext:
    """Object representing the arguments to distutils.core.setup()."""

    def __init__(self, pkgname, version, setup_file):
        self._working_dir = os.path.dirname(os.path.abspath(setup_file))
        self.version = version
        self.packages = []
        self.package_data = {}
        self.package_dir = {}
        self.ext_modules = []
        self.scripts = []
        self.platforms = None
        self.classifiers = None

    def setup(self):
        kwargs = self.__dict__.copy()
        for name in self.__dict__:
            if name[0] == "_":
                del kwargs[name]
        if "--debug" in sys.argv:
            import pprint
            pprint.pprint(kwargs)
        else:
            root_logger = logging.getLogger()
            if not root_logger.handlers:
                root_logger.addHandler(logging.StreamHandler())
            try:
                from setuptools import setup
            except ImportError:
                # package_data can't be handled this way ;-(
                if self.package_data:
                    _logger.error(
                        "can't import setuptools;"
                        " some package data will not be properly installed")
                from distutils.core import setup
            setup(**kwargs)

    def load_metadata(self, path):
        f = open(path, "rU")
        publication.load(f, metadata=self)
        if self.platforms:
            self.platforms = ", ".join(self.platforms)

    def scan_package(self, name, directory, reldir):
        # load the package metadata
        pkginfo = package.loadPackageInfo(name, directory, reldir)
        self.scripts.extend(pkginfo.script)
        self.ext_modules.extend(pkginfo.extensions)

        # scan the files in the directory:
        files = os.listdir(directory)
        for fn in files:
            fnbase, ext = os.path.splitext(fn)
            if ext in (".py", ".pyc", ".pyo", ".so", ".sl", ".pyd"):
                continue
            path = os.path.join(directory, fn)
            if os.path.isdir(path):
                init_py = os.path.join(path, "__init__.py")
                if os.path.isfile(init_py):
                    # if this package is published separately, skip it:
                    if os.path.isfile(os.path.join(path, "PUBLICATION.txt")):
                        continue
                    pkgname = "%s.%s" % (name, fn)
                    self.packages.append(pkgname)
                    self.scan_package(
                        pkgname, path, posixpath.join(reldir, fn))
                else:
                    # an ordinary directory
                    self.scan_directory(name, path, fn)
            else:
                self.add_package_file(name, fn)

    def scan_directory(self, pkgname, directory, reldir):
        """Scan a data directory, adding files to package_data."""
        for fn in os.listdir(directory):
            path = os.path.join(directory, fn)
            if os.path.isdir(path):
                self.scan_directory(pkgname,
                                    os.path.join(directory, fn),
                                    posixpath.join(reldir, fn))
            else:
                fnbase, ext = os.path.splitext(fn)
                if ext in (".pyc", ".pyo", ".so", ".sl", ".pyd"):
                    continue
                self.add_package_file(pkgname, posixpath.join(reldir, fn))

    def add_package_dir(self, pkgname, reldir):
        if pkgname.replace(".", posixpath.sep) != reldir:
            self.package_dir[pkgname] = reldir

    def add_package_file(self, pkgname, relfn):
        L = self.package_data.setdefault(pkgname, [])
        L.append(relfn)


class PackageContext(SetupContext):

    def __init__(self, pkgname, version, setup_file):
        SetupContext.__init__(self, pkgname, version, setup_file)
        self.packages.append(pkgname)
        self.load_metadata(
            os.path.join(self._working_dir, pkgname, "PUBLICATION.txt"))
        self.add_package_dir(pkgname, pkgname)
        self.scan_package(pkgname, os.path.join(self._working_dir, pkgname),
                          pkgname)


class CollectionContext(SetupContext):

    def __init__(self, pkgname, version, setup_file):
        SetupContext.__init__(self, pkgname, version, setup_file)
        self.load_metadata(os.path.join(self._working_dir,
                                        "PUBLICATION.txt"))
