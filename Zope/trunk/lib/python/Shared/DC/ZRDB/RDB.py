#!/bin/env python
############################################################################## 
#
#     Copyright 
#
#       Copyright 1996 Digital Creations, L.C., 910 Princess Anne
#       Street, Suite 300, Fredericksburg, Virginia 22401 U.S.A. All
#       rights reserved.
#
############################################################################## 
__doc__='''Class for reading RDB files


$Id: RDB.py,v 1.21 1998/12/16 15:10:22 jim Exp $'''
__version__='$Revision: 1.21 $'[11:-2]

import regex, regsub
from string import split, strip, lower, upper, atof, atoi, atol, find, join
import DateTime
from Missing import MV
from array import array
from Record import Record
from Acquisition import Implicit
import ExtensionClass

def parse_text(s):
    if find(s,'\\') < 0 and (find(s,'\\t') < 0 and find(s,'\\n') < 0): return s
    r=[]
    for x in split(s,'\\\\'):
	x=join(split(x,'\\n'),'\n')
	r.append(join(split(x,'\\t'),'\t'))
    return join(r,'\\')


Parsers={'n': atof,
	 'i': atoi,
	 'l': atol,
	 'd': DateTime.DateTime,
	 't': parse_text,
	 }


record_classes={}

class SQLAlias(ExtensionClass.Base):
    def __init__(self, name): self._n=name
    def __of__(self, parent): return getattr(parent, self._n)
 
class NoBrains: pass

class DatabaseResults:
    """Class for reading RDB files
    """
    _index=None

    def __init__(self,file,brains=NoBrains, parent=None):

	self._file=file
	readline=file.readline
	line=readline()
	self._parent=parent

	comment_pattern=regex.compile('#')
	while line and comment_pattern.match(line) >= 0: line=readline()

	line=line[:-1]
	if line and line[-1:] in '\r\n': line=line[:-1]
	self._names=names=split(line,'\t')
	if not names: raise ValueError, 'No column names'

        aliases=[]
	self._schema=schema={}
	i=0
	for name in names:
	    name=strip(name)
	    if not name:
		raise ValueError, 'Empty column name, %s' % name
	    if schema.has_key(name):
		raise ValueError, 'Duplicate column name, %s' % name
	    schema[name]=i
            n=lower(name)
            if n != name: aliases.append((n, SQLAlias(name)))
            n=upper(name)
            if n != name: aliases.append((n, SQLAlias(name)))
	    i=i+1

	self._nv=nv=len(names)
	line=readline()
	line=line[:-1]
	if line[-1:] in '\r\n': line=line[:-1]
	
	self._defs=defs=split(line,'\t')
	if not defs: raise ValueError, 'No column definitions'
	if len(defs) != nv:
	    raise ValueError, (
		"""The number of column names and the number of column
		definitions are different.""")
	
	i=0
	self._parsers=parsers=[]
	defre=regex.compile('\([0-9]*\)\([a-zA-Z]\)?')
	self._data_dictionary=dd={}
	self.__items__=items=[]
	for _def in defs:
	    _def=strip(_def)
	    if not _def:
		raise ValueError, ('Empty column definition for %s' % names[i])
	    if defre.match(_def) < 0:
		raise ValueError, (
		    'Invalid column definition for, %s, for %s'
		    % _def, names[i])
	    type=lower(defre.group(2))
	    width=defre.group(1)
	    if width: width=atoi(width)
	    else: width=8

	    try: parser=Parsers[type]
	    except: parser=str

	    name=names[i]
	    d={'name': name, 'type': type, 'width': width, 'parser': parser}
	    items.append(d)
	    dd[name]=d
	    
	    parsers.append(i,parser)
	    i=i+1

	# Create a record class to hold the records.
	names=tuple(names)
	if record_classes.has_key((names,brains)):
	    r=record_classes[names,brains]
	else:
	    class r(Record, Implicit, brains):
		'Result record class'		    

	    r.__record_schema__=schema
	    for k in filter(lambda k: k[:2]=='__', Record.__dict__.keys()):
		setattr(r,k,getattr(Record,k))
		record_classes[names,brains]=r

            # Add SQL Aliases
            d=r.__dict__
            for k, v in aliases:
                if not hasattr(r,k): d[k]=v

	    if hasattr(brains, '__init__'):
		binit=brains.__init__
		if hasattr(binit,'im_func'): binit=binit.im_func
		def __init__(self, data, parent, binit=binit):
		    Record.__init__(self,data)
		    binit(self.__of__(parent))

		r.__dict__['__init__']=__init__
		    

	self._class=r

	# OK, we've read meta data, now get line indexes

	p=file.tell()
	save=self._lines=array('i')
	save=save.append
	l=readline()
	while l:
	    save(p)
	    p=p+len(l)
	    l=readline()

    def _searchable_result_columns(self): return self.__items__
    def names(self): return self._names
    def data_dictionary(self): return self._data_dictionary

    def __len__(self): return len(self._lines)

    def __getitem__(self,index):
	if index==self._index: return self._row
	file=self._file
	file.seek(self._lines[index])
	line=file.readline()
	line=line[:-1]
	if line and line[-1:] in '\r\n': line=line[:-1]
	fields=split(line,'\t')
	l=len(fields)
	nv=self._nv
	if l != nv:
	    if l < nv:
		fields=fields+['']*(nv-l)
	    else:
		raise ValueError, (
		    """The number of items in record %s is invalid
		    <pre>%s\n%s\n%s\n%s</pre>
		    """ 
		    % (index, ('='*40), line, ('='*40), fields))
        for i, parser in self._parsers:
            try: v=parser(fields[i])
            except:
                if fields[i]:
                    raise ValueError, (
                        """Invalid value, %s, for %s in record %s"""
                        % (fields[i], self._names[i], index))
                else: v=MV
            fields[i]=v

	parent=self._parent
	fields=self._class(fields, parent)
	self._index=index
	self._row=fields
	if parent is None: return fields
	return fields.__of__(parent)

File=DatabaseResults
