#! /usr/bin/env python1.5

# runtest.py

import sys
import os
import string
from cStringIO import StringIO
import glob

import driver

def showdiff(a, b):
    import ndiff
    cruncher = ndiff.SequenceMatcher(ndiff.IS_LINE_JUNK, a, b)
    for tag, alo, ahi, blo, bhi in cruncher.get_opcodes():
        if tag == "equal":
            continue
        print nicerange(alo, ahi) + tag[0] + nicerange(blo, bhi)
        ndiff.dump('<', a, alo, ahi)
        if a and b:
            print '---'
        ndiff.dump('>', b, blo, bhi)

def nicerange(lo, hi):
    if hi <= lo+1:
        return str(lo+1)
    else:
        return "%d,%d" % (lo+1, hi)

def main():
    opts = []
    args = sys.argv[1:]
    while args and args[0][:1] == '-':
        opts.append(args[0])
        del args[0]
    if not args:
        args = glob.glob(os.path.join("test", "test*.xml"))
    for arg in args:
        print arg,
        sys.stdout.flush()
        save = sys.stdout, sys.argv
        try:
            sys.stdout = stdout = StringIO()
            sys.argv = [""] + opts + [arg]
            driver.main()
        finally:
            sys.stdout, sys.argv = save
        head, tail = os.path.split(arg)
        outfile = os.path.join(
            head,
            string.replace(tail, "test", "out"))
        try:
            f = open(outfile)
        except IOError:
            expected = None
            print "(missing file %s)" % outfile,
        else:
            expected = f.readlines()
            f.close()
        stdout.seek(0)
        if hasattr(stdout, "readlines"):
            actual = stdout.readlines()
        else:
            actual = readlines(stdout)
        if actual == expected:
            print "OK"
        else:
            print "not OK"
            if expected is not None:
                showdiff(expected, actual)

def readlines(f):
    L = []
    while 1:
        line = f.readline()
        if not line:
            break
        L.append(line)
    return L

if __name__ == "__main__":
    main()
