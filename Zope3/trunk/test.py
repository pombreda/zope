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
"""Run the test suite.

Usage: %(PROGRAM)s [options] [modfilter [testfilter]]
Options:

-b
    Run "python setup.py -q build" before running tests, where "python" is the
    version of python used to run test.py.  Highly recommended.  Tests will be
    run from the build directory.

-B
    Run "python setup.py -q build_ext -i" before running tests.  Tests will be
    run from the source directory.

-c
    Use pychecker.

-d
    Instead of the normal test harness, run a debug version which doesn't
    catch any exceptions.  This is occasionally handy when the unittest code
    catching the exception doesn't work right.  Unfortunately, the debug
    harness doesn't print the name of the test, so Use With Care.

-D
    Works like -d, except that it loads pdb when an exception occurs.

-g threshold
    Set the garbage collector generation0 threshold.  This can be used to
    stress memory and gc correctness.  Some crashes are only reproducible when
    the threshold is set to 1 (aggressive garbage collection).  Do "-g 0" to
    disable garbage collection altogether.

-G gc_option
    Set the garbage collection debugging flags.  The argument must be one of
    the DEBUG_ flags defined by the Python gc module.  Multiple options can be
    specified by using "-G OPTION1 -G OPTION2."

-h / --help
    Print this help text and exit.

-L
    Keep running the selected tests in a loop.  You may experience memory
    leakage, but this is a handy option for catching race conditions.

-u
-m
    Use the PyUnit GUI instead of output to the command line.  The GUI imports
    tests on its own, taking care to reload all dependencies on each run.  The
    debug (-d), verbose (-v), and Loop (-L) options will be ignored.  The
    testfilter filter is also not applied.  -m starts the gui minimized.

-p
    Show running progress.  It can be combined with -v or -vv.

-T
    Use the trace module from Python for code coverage.  XXX This only works
    if trace.py is explicitly added to PYTHONPATH.  The current utility writes
    coverage files to a directory named `coverage' that is parallel to
    `build'.  It also prints a summary to stdout.

-v
    Verbose output.  With one -v, unittest prints a dot (".") for each test
    run.  With -vv, unittest prints the name of each test (for some definition
    of "name" ...).  With no -v, unittest is silent until the end of the run,
    except when errors occur.

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

    test.py -vvb . "^checkWriteClient$"

    Builds the project silently, then runs unittest in verbose mode on all
    tests whose names are precisely "checkWriteClient".  Useful when
    debugging a specific test.

    test.py -vvb . "!^checkWriteClient$"

    As before, but runs all tests whose names aren't precisely
    "checkWriteClient".  Useful to avoid a specific failing test you don't
    want to deal with just yet.

    test.py -m . "!^checkWriteClient$"

    As before, but now opens up a minimized PyUnit GUI window (only showing
    the progressbar).  Double-clicking the progressbar will start the import
    and run all tests.  Useful for refactoring runs where you continually want
    to make sure all tests still pass.
"""

import gc
import os
import re
import pdb
import sys
import unittest
import linecache
import traceback
from os.path import join, commonprefix

from distutils.util import get_platform

PROGRAM = sys.argv[0]

# For Python's earlier than 2.2.2
try:
    True, False
except NameError:
    True = 1
    False = 0


# We know we're going to need this so import it now.  Python 2.2 does not come
# with the pyexpat library by default, although Python 2.3 will.
try:
    import xml.parsers.expat
except ImportError:
    print >> sys.stderr, "WARNING: the pyexpat module is required"
    raise

class ImmediateTestResult(unittest._TextTestResult):

    __super_init = unittest._TextTestResult.__init__
    __super_startTest = unittest._TextTestResult.startTest
    __super_printErrors = unittest._TextTestResult.printErrors

    def __init__(self, stream, descriptions, verbosity, debug=None,
                 count=None, progress=0):
        self.__super_init(stream, descriptions, verbosity)
        self._debug = debug
        self._progress = progress
        self._progressWithNames = 0
        self._count = count
        if progress and verbosity == 1:
            self.dots = 0
            self._progressWithNames = 1
            self._lastWidth = 0
            self._maxWidth = 80 # would be nice to determine terminal width
            self._maxWidth -= len('xxxx/xxxx (xxx.x%): ') + 1

    def stopTest(self, test):
        if gc.garbage:
            print test
            print gc.garbage
        
    def _print_traceback(self, msg, err, test, errlist):
        if self.showAll or self.dots:
            self.stream.writeln("\n")

        tb = ''.join(traceback.format_exception(*err))
        self.stream.writeln(msg)
        self.stream.writeln(tb)
        errlist.append((test, tb))

    def startTest(self, test):
        if self._progress:
            self.stream.write('\r%4d' % (self.testsRun + 1))
            if self._count:
                self.stream.write('/%d (%5.1f%%)' % (self._count,
                                  (self.testsRun + 1) * 100.0 / self._count))
            if self.showAll:
                self.stream.write(": ")
            elif self._progressWithNames:
                # XXX will break with multibyte strings
                name = self.getDescription(test)
                width = len(name)
                if width < self._lastWidth:
                    name += ' ' * (self._lastWidth - width)
                self.stream.write(': %s' % name[:self._maxWidth])
                self._lastWidth = width
            self.stream.flush()
        self.__super_startTest(test)

    def addError(self, test, err):
        if self._progress:
            self.stream.write('\r')
        if self._debug:
            raise err[0], err[1], err[2]
        self._print_traceback("Error in test %s" % test, err,
                              test, self.errors)

    def addFailure(self, test, err):
        if self._progress:
            self.stream.write('\r')
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
        debug = kwarg.get('debug')
        if debug is not None:
            del kwarg['debug']
        progress = kwarg.get('progress')
        if progress is not None:
            del kwarg['progress']
        self.__super_init(**kwarg)
        self._debug = debug
        self._progress = progress

    def _makeResult(self):
        return ImmediateTestResult(self.stream, self.descriptions,
                                   self.verbosity, debug=self._debug,
                                   count=self._count, progress=self._progress)

    def run(self, test):
        self._count = test.countTestCases()
        return unittest.TextTestRunner.run(self, test)

# setup list of directories to put on the path

def setup_path():
    DIRS = [join('lib','python'),
            ]
    cwd = os.getcwd()
    for d in DIRS:
        sys.path.insert(0, join(cwd, d))

def match(rx, s):
    if not rx:
        return 1
    if rx[0] == '!':
        return re.search(rx[1:], s) is None
    else:
        return re.search(rx, s) is not None

class TestFileFinder:
    def __init__(self, prefix):
        self.files = []
        self.prefix = prefix

    def visit(self, rx, dir, files):
        if not dir.endswith('tests'):
            return
        # ignore tests that aren't in packages
        if not "__init__.py" in files:
            if not files or files == ['CVS']:
                return
            print "not a package", dir
            return

        # ignore tests when the package can't be imported, possibly due to
        # dependency failures.
        pkg = dir[len(self.prefix)+1:].replace(os.sep, '.')
        try:
            __import__(pkg)
        # We specifically do not want to catch ImportError since that's useful
        # information to know when running the tests.
        except RuntimeError, e:
            print 'skipping', pkg, 'because:', e
            return

        for file in files:
            if file[:4] == "test" and file[-3:] == ".py":
                path = join(dir, file)
                if match(rx, path):
                    self.files.append(path)

def find_tests(rx):
    prefix = join('lib', 'python')
    finder = TestFileFinder(prefix)
    os.path.walk(prefix, finder.visit, rx)
    return finder.files

def package_import(modname):
    mod = __import__(modname)
    for part in modname.split(".")[1:]:
        mod = getattr(mod, part)
    return mod

def module_from_path(path):
    """Return the Python package name indiciated by the filesystem path."""

    assert path.endswith('.py')
    path = path[:-3]
    dirs = []
    while path:
        path, end = os.path.split(path)
        dirs.insert(0, end)
    return ".".join(dirs[2:])

def get_suite(file):
    modname = module_from_path(file)
    try:
        mod = package_import(modname)
    except ImportError, err:
        # print traceback
        print "Error importing %s\n%s" % (modname, err)
        print_tb_last()
        print
        if debug:
            raise
        return None
    try:
        suite_func = mod.test_suite
    except AttributeError:
        print "No test_suite() in %s" % file
        return None
    return suite_func()

def filter_testcases(s, rx):
    new = unittest.TestSuite()
    for test in s._tests:
        if isinstance(test, unittest.TestCase):
            name = test.id() # Full test name: package.module.class.method
            name = name[1 + name.rfind('.'):] # extract method name
            if match(rx, name):
                new.addTest(test)
        else:
            filtered = filter_testcases(test, rx)
            if filtered:
                new.addTest(filtered)
    return new

def gui_runner(files, test_filter):
    sys.path.insert(0, join(os.getcwd(), 'utilities'))
    import unittestgui
    suites = []
    for file in files:
        suites.append(module_from_path(file) + '.test_suite')

    suites = ", ".join(suites)
    minimal = (GUI == 'minimal')
    unittestgui.main(suites, minimal)

def runner(files, test_filter, debug):
    runner = ImmediateTestRunner(verbosity=VERBOSE, debug=debug,
                                 progress=progress)
    suite = unittest.TestSuite()
    for file in files:
        s = get_suite(file)
        if s is None:
            continue
        if test_filter is not None:
            s = filter_testcases(s, test_filter)
        suite.addTest(s)
    try:
        r = runner.run(suite)
    except:
        if debugger:
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

def main(module_filter, test_filter):
    os.path.walk(os.curdir, remove_stale_bytecode, None)
    setup_path()
    files = find_tests(module_filter)
    files.sort()

    if GUI:
        gui_runner(files, test_filter)
    elif LOOP:
        while 1:
            runner(files, test_filter, debug)
    elif TRACE:
        coverdir = os.path.join(os.getcwd(),"coverage")
        import trace
        tracer = trace.Trace(ignoredirs=[sys.prefix, sys.exec_prefix],
                             trace=0, count=1)
        tracer.runctx("runner(files, test_filter, debug)",
                      globals=globals(), locals=vars())
        r = tracer.results()
        r.write_results(show_missing=True, summary=True, coverdir=coverdir)
    else:
        runner(files, test_filter, debug)


def process_args(argv=None):
    if argv is None:
        argv = sys.argv
        
    import getopt
    global module_filter
    global test_filter
    global VERBOSE
    global LOOP
    global GUI
    global TRACE
    global debug
    global debugger
    global build
    global gcthresh
    global progress
    global build_inplace

    module_filter = None
    test_filter = None
    VERBOSE = 0
    LOOP = False
    GUI = 0
    TRACE = False
    # Don't collect test results; simply let tests crash
    debug = False
    debugger = False
    build = False
    build_inplace = False
    gcthresh = None
    gcflags = []
    progress = False

    try:
        opts, args = getopt.getopt(
            argv[1:], 'bBcdDg:G:hLumpTv',
            ['help'])
    except getopt.error, msg:
        print msg
        print "Try `python %s -h' for more information." % argv[0]
        sys.exit(2)

    for k, v in opts:
        if k == '-b':
            build = True
        elif k == '-B':
            build = build_inplace = True
        elif k == '-c':
            os.environ['PYCHECKER'] = "-q"
            import pychecker.checker
        elif k == '-d':
            debug = True
        elif k == '-D':
            debug = True
            debugger = True
        elif k == '-g':
            gcthresh = int(v)
        elif k == '-G':
            if not v.startswith("DEBUG_"):
                print "-G argument must be DEBUG_ flag, not", repr(v)
                sys.exit(1)
            gcflags.append(v)
        elif k in ('-h', '--help'):
            print __doc__ % globals()
            sys.exit(0)
        elif k == '-L':
            LOOP = True
        elif k == '-u':
            GUI = 1
        elif k == '-m':
            GUI = 'minimal'
        elif k == '-p':
            progress = True
        elif k == '-T':
            TRACE = True
        elif k == '-v':
            VERBOSE += 1

    if gcthresh is not None:
        gc.set_threshold(gcthresh)
        print 'gc threshold:', gc.get_threshold()

    if gcflags:
        import gc
        val = 0
        for flag in gcflags:
            v = getattr(gc, flag, None)
            if v is None:
                print "Unknown gc flag", repr(flag)
                print gc.set_debug.__doc__
                sys.exit(1)
            val |= v
        gc.set_debug(v)

    # XXX support not-build-in-place, when we get a setup.py
    if build:
        cmd = sys.executable + " stupid_build.py"
        if VERBOSE:
            print cmd
        sts = os.system(cmd)
        if sts:
            print "Build failed", hex(sts)
            sys.exit(1)

    if args:
        if len(args) > 1:
            test_filter = args[1]
        module_filter = args[0]
    try:
        bad = main(module_filter, test_filter)
        if bad:
            sys.exit(1)
    except ImportError, err:
        print err
        print sys.path
        raise



def print_tb_last():
    """Print up to 'limit' stack trace entries from the traceback 'tb'.

    If 'limit' is omitted or None, all entries are printed.  If 'file'
    is omitted or None, the output goes to sys.stderr; otherwise
    'file' should be an open file or file-like object with a write()
    method.
    """
    tb = sys.exc_info()[2]
    file = sys.stderr
    while 1:
        f = tb.tb_frame
        lineno = traceback.tb_lineno(tb)
        tb = tb.tb_next
        if tb is not None:
            continue

        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        file.write('  File "%s", line %d, in %s\n' % (filename,lineno,name))
        line = linecache.getline(filename, lineno)
        if line: file.write('    %s\n' % line.strip())
        break

if __name__ == "__main__":
    process_args()

# The following method is for debugging unit tests from a Python prompt:
def debug(args=""):
    """Debug your unit tests with the post mortem debugger.

    Just run the debug function with a string containing command-line
    arguments. (The function uses a cheesy parser, aka split. ;)

    For example, to debug the tests in package Zope.App.DublinCore::

      import test
      test.debug('Zope.App.DublinCore')

    At the first failure or error, an exception will be raised. At
    that point, you can use pdb's post-mortem debugger::

      import pdb
      pdb.pm()

    """    
    
    process_args(["", "-d"] + args.split())
    
