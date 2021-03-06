##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
import commands
import fnmatch
import os
import re
import sys

import pkg_resources

from z3c.dependencychecker import importchecker


ZCML_PACKAGE_PATTERN = re.compile(r"""
\s           # Whitespace.
package=     #
['\"]        # Single or double quote.
(?P<import>  # Start of 'import' variable.
\S+          # Non-whitespace string.
)            # End of 'import' variable.
['\"]        # Single or double quote.
""", re.VERBOSE)


def print_unused_imports(unused_imports):
    found = []
    for path in sorted(unused_imports.keys()):
        for (module, line_number) in unused_imports[path]:
            found.append((path, line_number, module))
    if found:
        print "Unused imports"
        print "=============="
        for (path, line_number, module) in found:
            print "%s:%s:  %s" % (path, line_number, module)
        print


def name_from_setup():
    cmd = "%s setup.py --name" % sys.executable
    name = commands.getoutput(cmd).strip()
    if 'traceback' in name.lower():
        print "You probably don't have setuptools installed globally"
        print "Or there's an error in your setup.py."
        print "Try running this by hand:"
        print cmd
        # Use buildout's setuptools_loc environ hack.
        sys.exit(1)
    return name


def existing_requirements():
    """Extract install and test requirements"""
    name = name_from_setup()
    # Who on earth made it so earth-shattering impossible to get your hands on
    # the egg info stuff via an api?  We'll do it mostly by hand...
    egginfo_dir_name = name + '.egg-info'
    if egginfo_dir_name in os.listdir(os.getcwd()):
        egginfo_dir = egginfo_dir_name
    else:
        egginfo_dir = os.path.join(os.getcwd(), 'src', egginfo_dir_name)
    requires_filename = os.path.join(egginfo_dir, 'requires.txt')
    if not os.path.exists(requires_filename):
        print "No %s found, exiting" % requires_filename
        sys.exit(1)
    lines = [line.strip() for line in open(requires_filename).readlines()]
    lines = [line for line in lines if line]
    install_required = []
    test_required = []
    for line in lines:
        if line.startswith('['):
            break
        req = pkg_resources.Requirement.parse(line)
        install_required.append(req.project_name)
    start = False
    for line in lines:
        if line == '[test]':
            start = True
            continue
        if not start:
            continue
        if line.startswith('['):
            break
        req = pkg_resources.Requirement.parse(line)
        test_required.append(req.project_name)

    # The project itself is of course both available and needed.
    install_required.append(name)

    # Distribute says it is setuptools.  Setuptools also includes
    # pkg_resources.
    if 'distribute' in install_required:
        install_required.append('setuptools')
    if 'setuptools' in install_required:
        install_required.append('pkg_resources')

    return (install_required, test_required)


def filter_missing(imports, required):
    missing = []
    for needed in imports:
        found = False
        for req in required:
            if req == needed:
                found = True
            if needed.startswith(req + '.'):
                # 're' should not match 'reinout.something', that's why we
                # check with an extra dot.
                found = True
        if not found:
            missing.append(needed)
    missing = sorted(set(missing))
    return missing


def filter_unneeded(imports, required):
    name = name_from_setup()
    imports.append(name) # We always use ourselves, obviously.
    imports = set(imports)
    required = set(required)
    setuptools_and_friends = set(
        ['distribute', 'setuptools', 'pkg_resources'])
    required = required - setuptools_and_friends

    unneeded = []
    for req in required:
        found = False
        for module in imports:
            if module.startswith(req):
                found = True
        if not found:
            unneeded.append(req)
    unneeded = sorted(set(unneeded))
    return unneeded


def _detect_modules(sample_module):
    sample_file = os.path.realpath(sample_module.__file__)
    stdlib_dir = os.path.dirname(sample_file)
    stdlib_extension = os.path.splitext(sample_file)[1]
    stdlib_files = os.listdir(stdlib_dir)
    modules = []
    for stdlib_file in stdlib_files:
        module, extension = os.path.splitext(stdlib_file)
        if extension == stdlib_extension:
            modules.append(module)
    if 'py' in stdlib_extension:
        # Also check directories with __init__.py* in them.
        init_file = '__init__' + stdlib_extension
        extra_modules = [name for name in os.listdir(stdlib_dir)
                         if os.path.exists(os.path.join(
                             stdlib_dir, name, init_file))]
        modules += extra_modules
    return modules


def stdlib_modules():
    py_module = os
    import datetime
    dynload_module = datetime
    modules = _detect_modules(py_module) + _detect_modules(dynload_module)
    modules.append('sys')
    return list(set(modules))


def includes_from_zcml(path):
    modules = []
    test_modules = []
    for path, dirs, files in os.walk(path):
        for zcml in [os.path.abspath(os.path.join(path, filename))
                     for filename in files
                     if fnmatch.fnmatch(filename, '*.zcml')]:
            contents = open(zcml).read()
            found = [module for module in
                     re.findall(ZCML_PACKAGE_PATTERN, contents)
                     if not module.startswith('.')]
            if 'test' in zcml:
                # ftesting.zcml, mostly.
                test_modules += found
            else:
                modules += found
    return modules, test_modules


def print_modules(modules, heading):
    if modules:
        print heading
        print '=' * len(heading)
        for module in modules:
            print "    ", module
        print


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        # Default
        path = os.path.join(os.getcwd(), 'src')
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        print "Unknown path:", path
        sys.exit(1)

    db = importchecker.ImportDatabase(path)
    # TODO: find zcml files
    db.findModules()
    unused_imports = db.getUnusedImports()
    test_imports = db.getImportedModuleNames(tests=True)
    install_imports = db.getImportedModuleNames(tests=False)
    (install_required, test_required) = existing_requirements()
    stdlib = stdlib_modules()
    (zcml_imports, zcml_test_imports) = includes_from_zcml(path)

    print_unused_imports(unused_imports)

    install_missing = filter_missing(install_imports + zcml_imports,
                                     install_required + stdlib)
    print_modules(install_missing, "Missing requirements")

    test_missing = filter_missing(test_imports + zcml_test_imports,
                                  install_required + test_required + stdlib)
    print_modules(test_missing, "Missing test requirements")

    install_unneeded = filter_unneeded(install_imports + zcml_imports,
                                       install_required)
    # See if one of ours is needed by the tests
    really_unneeded = filter_unneeded(test_imports + zcml_test_imports,
                                      install_unneeded)
    move_to_test = sorted(set(install_unneeded) - set(really_unneeded))

    print_modules(really_unneeded, "Unneeded requirements")
    print_modules(move_to_test,
                  "Requirements that should be test requirements")

    test_unneeded = filter_unneeded(test_imports + zcml_test_imports,
                                    test_required)
    print_modules(test_unneeded, "Unneeded test requirements")


    if install_missing or test_missing or install_unneeded or test_unneeded:
        print "Note: requirements are taken from the egginfo dir, so you need"
        print "to re-run buildout (or setup.py or whatever) for changes in "
        print "setup.py to have effect."
        print

    # TODO: report on unneeded requirements
