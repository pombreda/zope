"""Try to do all of the installation steps.

This must be run from the top-level directory of the installation.
(Yes, this is cheezy.  We'll fix this when we have a chance.

"""

import os
home=os.getcwd()
print
print '-'*78
print 'Compiling py files'
import compileall
compileall.compile_dir(os.getcwd())

import build_extensions

print
print '-'*78
print 'making the var directory'
os.chdir(home)
os.mkdir('var')
print
print '-'*78
print 'NOTE: change owndership or permissions on var so that it can be'
print '      writen by the web server!'
print
print "NOTE: The default super user name and password are 'superuser'"
print "      and '123'.  Create a file named 'access' in this directory"
print "      with a different super user name and password on one line"
print "      separated by a a colon. (e.g. 'spam:eggs').  You can also"
print "      specify a domain (e.g. 'spam:eggs:*.digicool.com')."
print '-'*78
print
print 'Done!'
