#! /usr/bin/env python2.3
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
test.py [-aBbcdDfgGhLmPprtTuv] [modfilter [testfilter]]

Find and run tests written using the unittest module.

The test runner searches for Python modules that contain test suites.
It collects those suites, and runs the tests.  There are many options
for controlling how the tests are run.  There are options for using
the debugger, reporting code coverage, and checking for refcount problems.

The test runner uses the following rules for finding tests to run.  It
searches for packages and modules that contain "tests" as a component
of the name, e.g. "frob.tests.nitz" matches this rule because tests is
a sub-package of frob.  Within each "tests" package, it looks for
modules that begin with the name "test."  For each test module, it
imports the module and calls the test_suite() method, which must
return a unittest TestSuite object.

-a level
--all
    Run the tests at the given level.  Any test at a level at or below
    this is run, any test at a level above this is not run.  Level 0
    runs all tests.  The default is to run tests at level 1.  --all is
    a shortcut for -a 0.

-b
--build
    Run "python setup.py build" before running tests, where "python"
    is the version of python used to run test.py.  Highly recommended.
    Tests will be run from the build directory.

-B
    Run "python setup.py build_ext -i" before running tests.  Tests will be
    run from the source directory.

-c  use pychecker

-d
    Instead of the normal test harness, run a debug version which
    doesn't catch any exceptions.  This is occasionally handy when the
    unittest code catching the exception doesn't work right.
    Unfortunately, the debug harness doesn't print the name of the
    test, so Use With Care.

--dir directory
    Option to limit where tests are searched for. This is important
    when you *really* want to limit the code that gets run.  This can
    be specified more than once to run tests in two different parts of
    the source tree.
    For example, if refactoring interfaces, you don't want to see the way
    you have broken setups for tests in other packages. You *just* want to
    run the interface tests.

-D
    Works like -d, except that it loads pdb when an exception occurs.

-f
    Run functional tests instead of unit tests.

-F
    Run both unit and functional tests.

-g threshold
    Set the garbage collector generation0 threshold.  This can be used
    to stress memory and gc correctness.  Some crashes are only
    reproducible when the threshold is set to 1 (agressive garbage
    collection).  Do "-g 0" to disable garbage collection altogether.

-G gc_option
    Set the garbage collection debugging flags.  The argument must be one
    of the DEBUG_ flags defined bythe Python gc module.  Multiple options
    can be specified by using "-G OPTION1 -G OPTION2."

--libdir test_root
    Search for tests starting in the specified start directory
    (useful for testing components being developed outside the main
    "src" or "build" trees).

--keepbytecode
    Do not delete all stale bytecode before running tests

-L
    Keep running the selected tests in a loop.  You may experience
    memory leakage.

-t
    Time the individual tests and print a list of the top 50, sorted from
    longest to shortest.

-P
    Run the tests under hotshot and display the top 50 stats, sorted by
    cumulative time and number of calls.

-p
    Show running progress.  It can be combined with -v or -vv.

-r
    Look for refcount problems.
    This requires that Python was built --with-pydebug.

-T
    Use the trace module from Python for code coverage.  The current
    utility writes coverage files to a directory named `coverage' that
    is parallel to `build'.  It also prints a summary to stdout.

-v
    Verbose output.  With one -v, unittest prints a dot (".") for each
    test run.  With -vv, unittest prints the name of each test (for
    some definition of "name" ...).  With no -v, unittest is silent
    until the end of the run, except when errors occur.

    When -p is also specified, the meaning of -v is slightly
    different.  With -p and no -v only the percent indicator is
    displayed.  With -p and -v the test name of the current test is
    shown to the right of the percent indicator.  With -p and -vv the
    test name is not truncated to fit into 80 columns and it is not
    cleared after the test finishes.

-u
-m
    Use the PyUnit GUI instead of output to the command line.  The GUI
    imports tests on its own, taking care to reload all dependencies
    on each run.  The debug (-d), verbose (-v), progress (-p), and
    Loop (-L) options will be ignored.  The testfilter filter is also
    not applied.

    -m starts the gui minimized.  Double-clicking the progress bar
    will start the import and run all tests.


modfilter
testfilter
    Case-sensitive regexps to limit which tests are run, used in search
    (not match) mode.
    In an extension of Python regexp notation, a leading "!" is stripped
    and causes the sense of the remaining regexp to be negated (so "!bc"
    matches any string that does not match "bc", and vice versa).
    By default these act like ".", i.e. nothing is excluded.

    modfilter is applied to a test file's path, starting at "build" and
    including (OS-dependent) path separators.

    testfilter is applied to the (method) name of the unittest methods
    contained in the test files whose paths modfilter matched.

Extreme (yet useful) examples:

    test.py -vvb . "^testWriteClient$"

    Builds the project silently, then runs unittest in verbose mode on all
    tests whose names are precisely "testWriteClient".  Useful when
    debugging a specific test.

    test.py -vvb . "!^testWriteClient$"

    As before, but runs all tests whose names aren't precisely
    "testWriteClient".  Useful to avoid a specific failing test you don't
    want to deal with just yet.

    test.py -m . "!^testWriteClient$"

    As before, but now opens up a minimized PyUnit GUI window (only showing
    the progress bar).  Useful for refactoring runs where you continually want
    to make sure all tests still pass.
"""

import gc
import hotshot, hotshot.stats
import os
import re
import pdb
import sys
import threading    # just to get at Thread objects created by tests
import time
import traceback
import unittest
import warnings

def set_trace_doctest(stdin=sys.stdin, stdout=sys.stdout, trace=pdb.set_trace):
    sys.stdin = stdin
    sys.stdout = stdout
    trace()

pdb.set_trace_doctest = set_trace_doctest

from distutils.util import get_platform

PLAT_SPEC = "%s-%s" % (get_platform(), sys.version[0:3])

class ImmediateTestResult(unittest._TextTestResult):

    __super_init = unittest._TextTestResult.__init__
    __super_startTest = unittest._TextTestResult.startTest
    __super_printErrors = unittest._TextTestResult.printErrors

    def __init__(self, stream, descriptions, verbosity, debug=False,
                 count=None, progress=False):
        self.__super_init(stream, descriptions, verbosity)
        self._debug = debug
        self._progress = progress
        self._progressWithNames = False
        self.count = count
        self._testtimes = {}
        if progress and verbosity == 1:
            self.dots = False
            self._progressWithNames = True
            self._lastWidth = 0
            self._maxWidth = 80
            try:
                import curses
            except ImportError:
                pass
            else:
                curses.setupterm()
                self._maxWidth = curses.tigetnum('cols')
            self._maxWidth -= len("xxxx/xxxx (xxx.x%): ") + 1

    def stopTest(self, test):
        self._testtimes[test] = time.time() - self._testtimes[test]
        if gc.garbage:
            print "The following test left garbage:"
            print test
            print gc.garbage
            # XXX Perhaps eat the garbage here, so that the garbage isn't
            #     printed for every subsequent test.

        # Did the test leave any new threads behind?
        new_threads = [t for t in threading.enumerate()
                         if (t.isAlive()
                             and
                             t not in self._threads)]
        if new_threads:
            print "The following test left new threads behind:"
            print test
            print "New thread(s):", new_threads

    def print_times(self, stream, count=None):
        results = self._testtimes.items()
        results.sort(lambda x, y: cmp(y[1], x[1]))
        if count:
            n = min(count, len(results))
            if n:
                print >>stream, "Top %d longest tests:" % n
        else:
            n = len(results)
        if not n:
            return
        for i in range(n):
            print >>stream, "%6dms" % int(results[i][1] * 1000), results[i][0]

    def _print_traceback(self, msg, err, test, errlist):
        if self.showAll or self.dots or self._progress:
            self.stream.writeln("\n")
            self._lastWidth = 0

        tb = "".join(traceback.format_exception(*err))
        self.stream.writeln(msg)
        self.stream.writeln(tb)
        errlist.append((test, tb))

    def startTest(self, test):
        if self._progress:
            self.stream.write("\r%4d" % (self.testsRun + 1))
            if self.count:
                self.stream.write("/%d (%5.1f%%)" % (self.count,
                                  (self.testsRun + 1) * 100.0 / self.count))
            if self.showAll:
                self.stream.write(": ")
            elif self._progressWithNames:
                # XXX will break with multibyte strings
                name = self.getShortDescription(test)
                width = len(name)
                if width < self._lastWidth:
                    name += " " * (self._lastWidth - width)
                self.stream.write(": %s" % name)
                self._lastWidth = width
            self.stream.flush()
        self._threads = threading.enumerate()
        self.__super_startTest(test)
        self._testtimes[test] = time.time()

    def getShortDescription(self, test):
        s = self.getDescription(test)
        if len(s) > self._maxWidth:
            pos = s.find(" (")
            if pos >= 0:
                w = self._maxWidth - (pos + 5)
                if w < 1:
                    # first portion (test method name) is too long
                    s = s[:self._maxWidth-3] + "..."
                else:
                    pre = s[:pos+2]
                    post = s[-w:]
                    s = "%s...%s" % (pre, post)
        return s[:self._maxWidth]

    def addError(self, test, err):
        if self._progress:
            self.stream.write("\r")
        if self._debug:
            raise err[0], err[1], err[2]
        self._print_traceback("Error in test %s" % test, err,
                              test, self.errors)

    def addFailure(self, test, err):
        if self._progress:
            self.stream.write("\r")
        if self._debug:
            raise err[0], err[1], err[2]
        self._print_traceback("Failure in test %s" % test, err,
                              test, self.failures)

    def printErrors(self):
        if self._progress and not (self.dots or self.showAll):
            self.stream.writeln()
        self.__super_printErrors()

    def printErrorList(self, flavor, errors):
        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln("%s: %s" % (flavor, self.getDescription(test)))
            self.stream.writeln(self.separator2)
            self.stream.writeln(err)


class ImmediateTestRunner(unittest.TextTestRunner):

    __super_init = unittest.TextTestRunner.__init__

    def __init__(self, **kwarg):
        debug = kwarg.get("debug")
        if debug is not None:
            del kwarg["debug"]
        progress = kwarg.get("progress")
        if progress is not None:
            del kwarg["progress"]
        profile = kwarg.get("profile")
        if profile is not None:
            del kwarg["profile"]
        self.__super_init(**kwarg)
        self._debug = debug
        self._progress = progress
        self._profile = profile
        # Create the test result here, so that we can add errors if
        # the test suite search process has problems.  The count
        # attribute must be set in run(), because we won't know the
        # count until all test suites have been found.
        self.result = ImmediateTestResult(
            self.stream, self.descriptions, self.verbosity, debug=self._debug,
            progress=self._progress)

    def _makeResult(self):
        # Needed base class run method.
        return self.result

    def run(self, test):
        self.result.count = test.countTestCases()
        if self._debug:
            club_debug(test)
        if self._profile:
            prof = hotshot.Profile("tests_profile.prof")
            args = (self, test)
            r = prof.runcall(unittest.TextTestRunner.run, *args)
            prof.close()
            stats = hotshot.stats.load("tests_profile.prof")
            stats.sort_stats('cumulative', 'calls')
            stats.print_stats(50)
            return r
        return unittest.TextTestRunner.run(self, test)

def club_debug(test):
    # Beat a debug flag into debug-aware test cases
    setDebugModeOn = getattr(test, 'setDebugModeOn', None)
    if setDebugModeOn is not None:
        setDebugModeOn()
        
    for subtest in getattr(test, '_tests', ()):
        club_debug(subtest)

# setup list of directories to put on the path
class PathInit:
    def __init__(self, build, build_inplace, libdir=None):
        self.inplace = None
        # Figure out if we should test in-place or test in-build.  If the -b
        # or -B option was given, test in the place we were told to build in.
        # Otherwise, we'll look for a build directory and if we find one,
        # we'll test there, otherwise we'll test in-place.
        if build:
            self.inplace = build_inplace
        if self.inplace is None:
            # Need to figure it out
            if os.path.isdir(os.path.join("build", "lib.%s" % PLAT_SPEC)):
                self.inplace = False
            else:
                self.inplace = True
        # Calculate which directories we're going to add to sys.path, and cd
        # to the appropriate working directory
        self.org_cwd = os.getcwd()
        if self.inplace:
            self.libdir = "src"
        else:
            self.libdir = "lib.%s" % PLAT_SPEC
            os.chdir("build")
        # Hack sys.path
        self.cwd = os.getcwd()
        sys.path.insert(0, os.path.join(self.cwd, self.libdir))
        # Hack again for external products.
        global functional
        kind = functional and "functional" or "unit"
        if libdir:
            extra = os.path.join(self.org_cwd, libdir)
            print "Running %s tests from %s" % (kind, extra)
            self.libdir = extra
            sys.path.insert(0, extra)
        else:
            print "Running %s tests from %s" % (kind, self.cwd)
        # Make sure functional tests find ftesting.zcml
        if functional:
            config_file = 'ftesting.zcml'
            if not self.inplace:
                # We chdired into build, so ftesting.zcml is in the
                # parent directory
                config_file = os.path.join('..', 'ftesting.zcml')
            print "Parsing %s" % config_file
            from zope.testing.functional import FunctionalTestSetup
            FunctionalTestSetup(config_file)

def match(rx, s):
    if not rx:
        return True
    if rx[0] == "!":
        return re.search(rx[1:], s) is None
    else:
        return re.search(rx, s) is not None

class TestFileFinder:
    def __init__(self, prefix):
        self.files = []
        self._plen = len(prefix)
        if not prefix.endswith(os.sep):
            self._plen += 1
        global functional
        if functional:
            self.dirname = "ftests"
        else:
            self.dirname = "tests"

    def visit(self, rx, dir, files):
        if os.path.split(dir)[1] != self.dirname:
            # Allow tests/ftests module rather than package.
            modfname = self.dirname + '.py'
            if modfname in files:
                path = os.path.join(dir, modfname)
                if match(rx, path):
                    self.files.append(path)
                    return
            return
        # ignore tests that aren't in packages
        if not "__init__.py" in files:
            if not files or files == ["CVS"]:
                return
            print "not a package", dir
            return

        # Put matching files in matches.  If matches is non-empty,
        # then make sure that the package is importable.
        matches = []
        for file in files:
            if file.startswith('test') and os.path.splitext(file)[-1] == '.py':
                path = os.path.join(dir, file)
                if match(rx, path):
                    matches.append(path)

        # ignore tests when the package can't be imported, possibly due to
        # dependency failures.
        pkg = dir[self._plen:].replace(os.sep, '.')
        try:
            __import__(pkg)
        # We specifically do not want to catch ImportError since that's useful
        # information to know when running the tests.
        except RuntimeError, e:
            if VERBOSE:
                print "skipping %s because: %s" % (pkg, e)
            return
        else:
            self.files.extend(matches)

    def module_from_path(self, path):
        """Return the Python package name indicated by the filesystem path."""
        assert path.endswith(".py")
        path = path[self._plen:-3]
        mod = path.replace(os.sep, ".")
        return mod

def walk_with_symlinks(top, func, arg):
    """Like os.path.walk, but follows symlinks on POSIX systems.

    This could theoreticaly result in an infinite loop, if you create symlink
    cycles in your Zope sandbox, so don't do that.
    """
    try:
        names = os.listdir(top)
    except os.error:
        return
    func(arg, top, names)
    exceptions = ('.', '..')
    for name in names:
        if name not in exceptions:
            name = os.path.join(top, name)
            if os.path.isdir(name):
                walk_with_symlinks(name, func, arg)

def find_test_dir(dir):
    if os.path.exists(dir):
        return dir
    d = os.path.join(pathinit.libdir, dir)
    if os.path.exists(d):
        if os.path.isdir(d):
            return d
        raise ValueError("%s does not exist and %s is not a directory"
                         % (dir, d))
    raise ValueError("%s does not exist!" % dir)

def find_tests(rx):
    global finder
    finder = TestFileFinder(pathinit.libdir)

    if test_dirs:
        for d in test_dirs:
            d = find_test_dir(d)
            walk_with_symlinks(d, finder.visit, rx)
    else:
        walk_with_symlinks(pathinit.libdir, finder.visit, rx)
    return finder.files

def package_import(modname):
    mod = __import__(modname)
    for part in modname.split(".")[1:]:
        mod = getattr(mod, part)
    return mod

class PseudoTestCase:
    """Minimal test case objects to create error reports.

    If test.py finds something that looks like it should be a test but
    can't load it or find its test suite, it will report an error
    using a PseudoTestCase.
    """

    def __init__(self, name, descr=None):
        self.name = name
        self.descr = descr

    def shortDescription(self):
        return self.descr

    def __str__(self):
        return "Invalid Test (%s)" % self.name

def get_suite(file, result):
    modname = finder.module_from_path(file)
    try:
        mod = package_import(modname)
        return mod.test_suite()
    except:
        result.addError(PseudoTestCase(modname), sys.exc_info())
        return None

def filter_testcases(s, rx):
    new = unittest.TestSuite()
    for test in s._tests:
        # See if the levels match
        dolevel = (level == 0) or level >= getattr(test, "level", 0)
        if not dolevel:
            continue
        if isinstance(test, unittest.TestCase):
            name = test.id() # Full test name: package.module.class.method
            name = name[1 + name.rfind("."):] # extract method name
            if not rx or match(rx, name):
                new.addTest(test)
        else:
            filtered = filter_testcases(test, rx)
            if filtered:
                new.addTest(filtered)
    return new

def gui_runner(files, test_filter):
    if build_inplace:
        utildir = os.path.join(os.getcwd(), "utilities")
    else:
        utildir = os.path.join(os.getcwd(), "..", "utilities")
    sys.path.append(utildir)
    import unittestgui
    suites = []
    for file in files:
        suites.append(finder.module_from_path(file) + ".test_suite")

    suites = ", ".join(suites)
    minimal = (GUI == "minimal")
    unittestgui.main(suites, minimal)

class TrackRefs:
    """Object to track reference counts across test runs."""

    def __init__(self):
        self.type2count = {}
        self.type2all = {}

    def update(self):
        obs = sys.getobjects(0)
        type2count = {}
        type2all = {}
        for o in obs:
            all = sys.getrefcount(o)

            if type(o) is str and o == '<dummy key>':
                # avoid dictionary madness
                continue
            t = type(o)
            if t in type2count:
                type2count[t] += 1
                type2all[t] += all
            else:
                type2count[t] = 1
                type2all[t] = all

        ct = [(type2count[t] - self.type2count.get(t, 0),
               type2all[t] - self.type2all.get(t, 0),
               t)
              for t in type2count.iterkeys()]
        ct.sort()
        ct.reverse()
        printed = False
        for delta1, delta2, t in ct:
            if delta1 or delta2:
                if not printed:
                    print "%-55s %8s %8s" % ('', 'insts', 'refs')
                    printed = True
                print "%-55s %8d %8d" % (t, delta1, delta2)

        self.type2count = type2count
        self.type2all = type2all

def runner(files, test_filter, debug):
    runner = ImmediateTestRunner(verbosity=VERBOSE, debug=debug,
                                 progress=progress, profile=profile,
                                 descriptions=False)
    suite = unittest.TestSuite()
    for file in files:
        s = get_suite(file, runner.result)
        # See if the levels match
        dolevel = (level == 0) or level >= getattr(s, "level", 0)
        if s is not None and dolevel:
            s = filter_testcases(s, test_filter)
            suite.addTest(s)
    try:
        r = runner.run(suite)
        if timesfn:
            r.print_times(open(timesfn, "w"))
            if VERBOSE:
                print "Wrote timing data to", timesfn
        if timetests:
            r.print_times(sys.stdout, timetests)
    except:
        if debugger:
            print "%s:" % (sys.exc_info()[0], )
            print sys.exc_info()[1]
            pdb.post_mortem(sys.exc_info()[2])
        else:
            raise

def remove_stale_bytecode(arg, dirname, names):
    names = map(os.path.normcase, names)
    for name in names:
        if name.endswith(".pyc") or name.endswith(".pyo"):
            srcname = name[:-1]
            if srcname not in names:
                fullname = os.path.join(dirname, name)
                print "Removing stale bytecode file", fullname
                os.unlink(fullname)

def main(module_filter, test_filter, libdir):
    if not keepStaleBytecode:
        os.path.walk(os.curdir, remove_stale_bytecode, None)

    # Get the log.ini file from the current directory instead of possibly
    # buried in the build directory.  XXX This isn't perfect because if
    # log.ini specifies a log file, it'll be relative to the build directory.
    # Hmm...
    logini = os.path.abspath("log.ini")

    # Initialize the path and cwd
    global pathinit
    pathinit = PathInit(build, build_inplace, libdir)

    # Initialize the logging module.

    import logging.config
    logging.basicConfig()

    level = os.getenv("LOGGING")
    if level:
        level = int(level)
    else:
        level = logging.CRITICAL
    logging.root.setLevel(level)

    if os.path.exists(logini):
        logging.config.fileConfig(logini)

    files = find_tests(module_filter)
    files.sort()

    if GUI:
        gui_runner(files, test_filter)
    elif LOOP:
        if REFCOUNT:
            rc = sys.gettotalrefcount()
            track = TrackRefs()
        while True:
            runner(files, test_filter, debug)
            gc.collect()
            if gc.garbage:
                print "GARBAGE:", len(gc.garbage), gc.garbage
                return
            if REFCOUNT:
                prev = rc
                rc = sys.gettotalrefcount()
                print "totalrefcount=%-8d change=%-6d" % (rc, rc - prev)
                track.update()
    else:
        runner(files, test_filter, debug)

    os.chdir(pathinit.org_cwd)


def process_args(argv=None):
    import getopt
    global module_filter
    global test_filter
    global VERBOSE
    global LOOP
    global GUI
    global TRACE
    global REFCOUNT
    global debug
    global debugger
    global build
    global level
    global libdir
    global timesfn
    global timetests
    global progress
    global build_inplace
    global keepStaleBytecode
    global test_dirs
    global profile

    if argv is None:
        argv = sys.argv

    module_filter = None
    test_filter = None
    VERBOSE = 0
    LOOP = False
    GUI = False
    TRACE = False
    REFCOUNT = False
    debug = False # Don't collect test results; simply let tests crash
    debugger = False
    build = False
    build_inplace = False
    gcthresh = None
    gcdebug = 0
    gcflags = []
    level = 1
    libdir = None
    progress = False
    timesfn = None
    timetests = 0
    keepStaleBytecode = 0
    kinds = 'unit'
    test_dirs = []
    profile = False

    try:
        opts, args = getopt.getopt(argv[1:], "a:bBcdDfFg:G:hLmPprtTuv",
                                   ["all", "help", "libdir=", "times=",
                                    "keepbytecode", "dir=", "build"])
    except getopt.error, msg:
        print msg
        print "Try `python %s -h' for more information." % argv[0]
        sys.exit(2)

    for k, v in opts:
        if k == "-a":
            level = int(v)
        elif k == "--all":
            level = 0
            os.environ["COMPLAIN_IF_TESTS_MISSED"]='1'
        elif k in ("-b", "--build"):
            build = True
        elif k == "-B":
            build = build_inplace = True
        elif k == "-c":
            # make sure you have a recent version of pychecker
            if not os.environ.get("PYCHECKER"):
                os.environ["PYCHECKER"] = "-q"
            import pychecker.checker
        elif k == "-d":
            debug = True
        elif k == "-D":
            debug = True
            debugger = True
        elif k == "-f":
            kinds = "functional"
        elif k == "-F":
            kinds = "all"
        elif k in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        elif k == "-g":
            gcthresh = int(v)
        elif k == "-G":
            if not v.startswith("DEBUG_"):
                print "-G argument must be DEBUG_ flag, not", repr(v)
                sys.exit(1)
            gcflags.append(v)
        elif k == '--keepbytecode':
            keepStaleBytecode = 1
        elif k == '--libdir':
            libdir = v
        elif k == "-L":
            LOOP = 1
        elif k == "-m":
            GUI = "minimal"
        elif k == "-P":
            profile = True
        elif k == "-p":
            progress = True
        elif k == "-r":
            if hasattr(sys, "gettotalrefcount"):
                REFCOUNT = True
            else:
                print "-r ignored, because it needs a debug build of Python"
        elif k == "-T":
            TRACE = True
        elif k == "-t":
            if not timetests:
                timetests = 50
        elif k == "-u":
            GUI = 1
        elif k == "-v":
            VERBOSE += 1
        elif k == "--times":
            try:
                timetests = int(v)
            except ValueError:
                # must be a filename to write
                timesfn = v
        elif k == '--dir':
            test_dirs.append(v)

    if sys.version_info < ( 2,3,2 ):
	print """\
	ERROR: Your python version is not supported by Zope3.
	Zope3 needs Python 2.3.2 or greater. You are running:""" + sys.version
	sys.exit(1)

    if gcthresh is not None:
        if gcthresh == 0:
            gc.disable()
            print "gc disabled"
        else:
            gc.set_threshold(gcthresh)
            print "gc threshold:", gc.get_threshold()

    if gcflags:
        val = 0
        for flag in gcflags:
            v = getattr(gc, flag, None)
            if v is None:
                print "Unknown gc flag", repr(flag)
                print gc.set_debug.__doc__
                sys.exit(1)
            val |= v
        gcdebug |= v

    if gcdebug:
        gc.set_debug(gcdebug)

    if build:
        # Python 2.3 is more sane in its non -q output
        if sys.hexversion >= 0x02030000:
            qflag = ""
        else:
            qflag = "-q"
        cmd = sys.executable + " setup.py " + qflag + " build"
        if build_inplace:
            cmd += "_ext -i"
        if VERBOSE:
            print cmd
        sts = os.system(cmd)
        if sts:
            print "Build failed", hex(sts)
            sys.exit(1)

    if kinds == "unit":
        k = [False]
    elif kinds == "functional":
        k = [True]
    elif kinds == "all":
        k = [False, True]
    
    global functional
    for functional in k:
        
        if VERBOSE:
            kind = functional and "functional" or "unit"
            if level == 0:
                print "Running %s tests at all levels" % kind
            else:
                print "Running %s tests at level %d" % (kind, level)

        # XXX We want to change *visible* warnings into errors.  The next
        # line changes all warnings into errors, including warnings we
        # normally never see.  In particular, test_datetime does some
        # short-integer arithmetic that overflows to long ints, and, by
        # default, Python doesn't display the overflow warning that can
        # be enabled when this happens.  The next line turns that into an
        # error instead.  Guido suggests that a better to get what we're
        # after is to replace warnings.showwarning() with our own thing
        # that raises an error.
        ## warnings.filterwarnings("error")
        warnings.filterwarnings("ignore", module="logging")

        if args:
            if len(args) > 1:
                test_filter = args[1]
            module_filter = args[0]
        try:
            if TRACE:
                # if the trace module is used, then we don't exit with
                # status if on a false return value from main.
                coverdir = os.path.join(os.getcwd(), "coverage")
                import trace
                ignoremods = ["os", "posixpath", "stat"]
                tracer = trace.Trace(ignoredirs=[sys.prefix, sys.exec_prefix],
                                     ignoremods=ignoremods,
                                     trace=False, count=True)

                tracer.runctx("main(module_filter, test_filter, libdir)",
                              globals=globals(), locals=vars())
                r = tracer.results()
                path = "/tmp/trace.%s" % os.getpid()
                import cPickle
                f = open(path, "wb")
                cPickle.dump(r, f)
                f.close()
                print path
                r.write_results(show_missing=True, summary=True, coverdir=coverdir)
            else:
                bad = main(module_filter, test_filter, libdir)
                if bad:
                    sys.exit(1)
        except ImportError, err:
            print err
            print sys.path
            raise


if __name__ == "__main__":
    process_args()
