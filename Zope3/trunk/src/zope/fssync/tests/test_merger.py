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
"""Tests for the Merger class.

$Id: test_merger.py,v 1.9 2003/05/15 12:05:12 gvanrossum Exp $
"""

import os
import shutil
import unittest
import tempfile

from os.path import exists, isdir, isfile, realpath, normcase

from zope.fssync.merger import Merger

class MockMetadatabase(object):

    def __init__(self):
        self.database = {}

    def makekey(self, file):
        file = realpath(file)
        key = normcase(file)
        return key, file

    def getentry(self, file):
        key, file = self.makekey(file)
        if key not in self.database:
            self.database[key] = {}
        return self.database[key]

    def setmetadata(self, file, metadata={}):
        key, file = self.makekey(file)
        if key not in self.database:
            self.database[key] = {"path": file}
        self.database[key].update(metadata)

    def delmetadata(self, file):
        key, file = self.makekey(file)
        if key in self.database:
            del self.database[key]

added = {"flag": "added"}
removed = {"flag": "removed"}

class TestMerger(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        # Create a list of temporary files to clean up at the end
        self.tempfiles = []

    def tearDown(self):
        # Clean up temporary files (or directories)
        for fn in self.tempfiles:
            if isdir(fn):
                shutil.rmtree(fn)
            elif isfile(fn):
                os.remove(fn)
        unittest.TestCase.tearDown(self)

    def addfile(self, data, suffix="", mode="w"):
        # Register a temporary file; write data to it if given
        file = tempfile.mktemp(suffix)
        self.tempfiles.append(file)
        if data is not None:
            f = open(file, mode)
            try:
                f.write(data)
            finally:
                f.close()
        return file

    def cmpfile(self, file1, file2, mode="r"):
        # Compare two files; they must exist
        f1 = open(file1, mode)
        try:
            data1 = f1.read()
        finally:
            f1.close()
        f2 = open(file2, mode)
        try:
            data2 = f2.read()
        finally:
            f2.close()
        return data1 == data2

    diff3ok = None

    def check_for_diff3(self):
        if self.diff3ok is None:
            self.__class__.diff3ok = self.diff3_check()
        return self.diff3ok

    def diff3_check(self):
        if not hasattr(os, "popen"):
            return False
        f1 = self.addfile("a")
        f2 = self.addfile("b")
        f3 = self.addfile("b")
        pipe = os.popen("diff3 -m -E %s %s %s" % (f1, f2, f3), "r")
        output = pipe.read()
        sts = pipe.close()
        return output == "b" and not sts

    def runtest(self, localdata, origdata, remotedata,
                localmetadata, remotemetadata, exp_localdata,
                exp_action, exp_state, exp_merge_state=None):
        local = self.addfile(localdata)
        orig = self.addfile(origdata)
        remote = self.addfile(remotedata)
        md = MockMetadatabase()
        if localmetadata is not None:
            md.setmetadata(local, localmetadata)
        if remotemetadata is not None:
            md.setmetadata(remote, remotemetadata)
        m = Merger(md)
        action, state = m.classify_files(local, orig, remote)
        self.assertEqual((action, state), (exp_action, exp_state))

        # Now try the actual merge
        state = m.merge_files(local, orig, remote, action, state)
        self.assertEqual(state, exp_merge_state or exp_state)
        self.assert_(md.getentry(remote).get("flag") is None)
        if exp_localdata is None:
            self.assert_(not exists(local))
        else:
            f = open(local, "r")
            try:
                data = f.read()
            finally:
                f.close()
            if exp_merge_state != "Conflict":
                self.assertEqual(data, exp_localdata)
            else:
                self.assert_(data.find(exp_localdata) >= 0)

        # Verify that the returned state matches reality
        if state == "Uptodate":
            self.assert_(self.cmpfile(local, orig))
            self.assert_(self.cmpfile(orig, remote))
            self.assert_(md.getentry(local))
            self.assert_(not md.getentry(local).get("flag"),
                         md.getentry(local))
            self.assert_(md.getentry(remote))
        elif state == "Modified":
            self.assert_(not self.cmpfile(local, orig))
            self.assert_(self.cmpfile(orig, remote))
            self.assert_(md.getentry(local))
            self.assert_(not md.getentry(local).get("flag"))
            self.assert_(md.getentry(remote))
        elif state == "Added":
            self.assert_(exists(local))
            self.assert_(not exists(orig))
            self.assert_(not exists(remote))
            self.assert_(not md.getentry(remote))
            self.assert_(md.getentry(local).get("flag") == "added")
        elif state == "Removed":
            self.assert_(not exists(local))
            self.assert_(self.cmpfile(orig, remote))
            self.assert_(md.getentry(local).get("flag") == "removed")
            self.assert_(md.getentry(remote))
        elif state == "Nonexistent":
            self.assert_(not exists(local))
            self.assert_(not exists(orig))
            self.assert_(not exists(remote))
            self.assert_(not md.getentry(local))
            self.assert_(not md.getentry(remote))
        elif state == "Conflict":
            self.assert_(md.getentry(local).has_key("conflict"))
            # No other checks; there are many kinds of conflicts
        elif state == "Spurious":
            self.assert_(exists(local))
            # Don't care about orig
            self.assert_(not exists(remote))
            self.assert_(not md.getentry(local))
            self.assert_(not md.getentry(remote))
        else:
            self.assert_(False)

    # Test cases for files

    def test_all_equal(self):
        self.runtest("a", "a", "a", {}, {}, "a", "Nothing", "Uptodate")

    def test_local_modified(self):
        self.runtest("ab", "a", "a", {}, {}, "ab", "Nothing", "Modified")

    def test_remote_modified(self):
        self.runtest("a", "a", "ab", {}, {}, "ab", "Copy", "Uptodate")

    def test_both_modified_resolved(self):
        if not self.check_for_diff3():
            return
        self.runtest("l\na\n", "a\n", "a\nr\n", {}, {},
                     "l\na\nr\n", "Merge", "Modified")

    def test_both_modified_conflict(self):
        if not self.check_for_diff3():
            return
        self.runtest("ab", "a", "ac", {}, {},
                     "", "Merge", "Modified", "Conflict")

    def test_local_added(self):
        self.runtest("a", None, None, added, None, "a", "Nothing", "Added")

    def test_remote_added(self):
        self.runtest(None, None, "a", None, {}, "a", "Copy", "Uptodate")

    def test_both_added_same(self):
        self.runtest("a", None, "a", added, {}, "a", "Fix", "Uptodate")

    def test_both_added_different(self):
        if not self.check_for_diff3():
            return
        self.runtest("a", None, "b", added, {},
                     "", "Merge", "Modified", "Conflict")

    def test_local_removed(self):
        self.runtest(None, "a", "a", removed, {}, None, "Nothing", "Removed")

    def test_remote_removed(self):
        self.runtest("a", "a", None, {}, None, None, "Delete", "Nonexistent")

    def test_both_removed(self):
        self.runtest(None, "a", None, removed, None,
                     None, "Delete", "Nonexistent")

    def test_local_lost_remote_unchanged(self):
        self.runtest(None, "a", "a", {}, {}, "a", "Copy", "Uptodate")

    def test_local_lost_remote_modified(self):
        self.runtest(None, "a", "b", {}, {}, "b", "Copy", "Uptodate")

    def test_local_lost_remote_removed(self):
        self.runtest(None, "a", None, {}, None, None, "Delete", "Nonexistent")

    def test_spurious(self):
        self.runtest("a", None, None, None, None, "a", "Nothing", "Spurious")

    # XXX need test cases for anomalies, e.g. files missing or present
    # in spite of metadata, or directories instead of files, etc.

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(TestMerger)

def test_main():
    unittest.TextTestRunner().run(test_suite())

if __name__=='__main__':
    test_main()
