#!/bin/env python
############################################################################## 
#
#     Copyright 
#
#       Copyright 1997 Digital Creations, L.C., 910 Princess Anne
#       Street, Suite 300, Fredericksburg, Virginia 22401 U.S.A. All
#       rights reserved. 
#
############################################################################## 

'''This module implements a simple item mix-in for objects that have a
very simple (e.g. one-screen) management interface, like documents,
Aqueduct database adapters, etc.

This module can also be used as a simple template for implementing new
item types. 

$Id: SimpleItem.py,v 1.6 1997/11/11 21:25:29 brian Exp $'''
__version__='$Revision: 1.6 $'[11:-2]

import Globals
from DateTime import DateTime
from CopySupport import CopySource


class Item(CopySource):

    # Name, relative to SOFTWARE_URL of icon used to display item
    # in folder listings.
    icon='App/arrow.jpg'

    # Meta type used for selecting all objects of a given type.
    meta_type='simple item'

    # Default title.  
    title=''

    # Empty manage_options signals that this object has a
    # single-screen management interface.
    manage_options=()

    # Utility that returns the title if it is not blank and the id
    # otherwise.
    def title_or_id(self):
	return self.title or self.id

    # Utility that returns the title if it is not blank and the id
    # otherwise.  If the title is not blank, then the id is included
    # in parens.
    def title_and_id(self):
	t=self.title
	return t and ("%s (%s)" % (t,self.id)) or self.id

    
    # Handy way to talk to ourselves in document templates.
    def this(self):
	return self

    # Interact with tree tag
    def tpURL(self):
	url=self.id
	if hasattr(url,'im_func'): url=url()
	return url

    def tpValues(self): return ()

    _manage_editedDialog=Globals.HTMLFile('OFS/editedDialog')
    def manage_editedDialog(self, REQUEST, **args):
	return apply(self._manage_editedDialog,(self, REQUEST), args)

    def bobobase_modification_time(self):
	try:
	    t=self._p_mtime
	    if t is None: return DateTime()
	except: t=0
	return DateTime(t)

    def modified_in_session(self):
	jar=self._p_jar
	if jar is None:
	    if hasattr(self, 'aq_parent') and hasattr(self.aq_parent, '_p_jar'):
		jar=self.aq_parent._p_jar
	    if jar is None: return 0
	if not jar.name: return 0
	try: jar.db[self._p_oid]
	except: return 0
	return 1


class Item_w__name__(Item):

    # Utility that returns the title if it is not blank and the id
    # otherwise.
    def title_or_id(self):
	return self.title or self.__name__

    # Utility that returns the title if it is not blank and the id
    # otherwise.  If the title is not blank, then the id is included
    # in parens.
    def title_and_id(self):
	t=self.title
	return t and ("%s (%s)" % (t,self.__name__)) or self.__name__

    def _setId(self, id):
	self.__name__=id

############################################################################## 
#
# $Log: SimpleItem.py,v $
# Revision 1.6  1997/11/11 21:25:29  brian
# Added copy/paste support, restricted unpickling, fixed DraftFolder bug
#
# Revision 1.5  1997/11/11 19:26:09  jim
# Fixed bug in modified_in_session.
#
# Revision 1.4  1997/11/10 14:55:14  jim
# Added two new methods, bobobase_modification_time, and
# modified_in_session, to support flagging new and session objects.
#
# Revision 1.3  1997/11/06 18:41:56  jim
# Added manage_editedDialog.
#
# Revision 1.2  1997/10/30 19:51:09  jim
# Added methods to support tree browsing.
#
# Revision 1.1  1997/09/10 18:42:36  jim
# Added SimpleItem mix-in and new title/id methods.
#
#
