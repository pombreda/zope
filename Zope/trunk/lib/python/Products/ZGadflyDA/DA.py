database_type='Gadfly'
########################################################################### 
#
#     Copyright 
#
#       Copyright 1996 Digital Creations, L.C., 910 Princess Anne
#       Street, Suite 300, Fredericksburg, Virginia 22401 U.S.A. All
#       rights reserved.
#
########################################################################### 
__doc__='''%s Database Connection

$Id: DA.py,v 1.1 1998/04/15 15:10:37 jim Exp $''' % database_type
__version__='$Revision: 1.1 $'[11:-2]

from db import DB, manage_DataSources
import sys, DABase, Globals

_connections={}

def data_sources():
    return filter(lambda ds, used=_connections.has_key: not used(ds[0]),
		  manage_DataSources())

addConnectionForm=Globals.HTMLFile('connectionAdd',globals())
def manage_addAqueductGadflyConnection(
    self, id, title, connection, check=None, REQUEST=None):
    """Add a DB connection to a folder"""
    self._setObject(id, Connection(
	id, title, connection, check))
    if REQUEST is not None: return self.manage_main(self,REQUEST)
    return self.manage_main(self,REQUEST)	

class Connection(DABase.Connection):
    database_type=database_type
    id='%s_database_connection' % database_type
    meta_type=title='Aqueduct %s Database Connection' % database_type
    icon='misc_/Aqueduct%s/conn' % database_type

    def factory(self): return DB

    def connect(self,s):
	c=_connections
	if c.has_key(s) and c[s] != self._p_oid:
	    raise 'In Use', (
		'The database <em>%s</em> is in use.' % s)
	c[s]=self._p_oid
	return Connection.inheritedAttribute('connect')(self, s)

    def __del__(self):
	s=self.connection_string
	c=_connections
	if c.has_key(s) and c[s] == self._p_oid: del c[s]

    def manage_close_connection(self, REQUEST):
	" "
	s=self.connection_string
	c=_connections
	if c.has_key(s) and c[s] == self._p_oid: del c[s]
	return Connection.inheritedAttribute('manage_close_connection')(self, REQUEST)
	

############################################################################## 
#
# $Log: DA.py,v $
# Revision 1.1  1998/04/15 15:10:37  jim
# initial
#
