"""Document object"""

__version__='$Revision: 1.22 $'[11:-2]

from Globals import HTML, HTMLFile,MessageDialog
from string import join,split,strip,rfind,atoi
from AccessControl.Role import RoleManager
import SimpleItem, regex




class Document(HTML, RoleManager, SimpleItem.Item_w__name__):
    """Document object"""
    meta_type      ='Document'
    icon           ='OFS/Document_icon.gif'
    __state_names__=HTML.__state_names__+('title','__roles__')

    def initvars(self, mapping, vars):
	"""Hook to override signature so we can detect whether we are
	running from the web"""
	HTML.initvars(self, mapping, vars)
	self.func_code.__init__(('self','REQUEST','RESPONSE'))
	self.func_defaults=(None,)

    def __call__(self, client=None, REQUEST={}, RESPONSE=None, **kw):
	kw['document_id']   =self.id
        kw['document_title']=self.title
	r=apply(HTML.__call__, (self, client, REQUEST), kw)
	if RESPONSE is None: return r
	return decapitate(r, RESPONSE)

    def validate(self, inst, parent, name, value, md):
	if hasattr(value, '__roles__'):
	    roles=value.__roles__
	elif inst is parent:
	    return 1
	else:
	    if str(name)[:6]=='manage': return 0
	    if hasattr(parent,'__roles__'): roles=parent.__roles__
	    elif hasattr(parent, 'aq_acquire'):
		try: roles=parent.aq_acquire('__roles__')
		except AttributeError: return 0
	    else: return 0
	if roles is None: return 1
	try: return md.AUTHENTICATED_USER.hasRole(roles)
	except AttributeError: return 0

    manage_editForm=HTMLFile('OFS/documentEdit')
    manage=manage_editDocument=manage_editForm

    def manage_edit(self,data,title,acl_type='A',acl_roles=[],SUBMIT='Change',
		    dtpref_cols='50',dtpref_rows='20',REQUEST=None):
	"""Edit method"""
        if SUBMIT=='Smaller':
            rows=atoi(dtpref_rows)-5
            cols=atoi(dtpref_cols)-5
	    e='Friday, 31-Dec-99 23:59:59 GMT'
	    resp=REQUEST['RESPONSE']
	    resp.setCookie('dtpref_rows',str(rows),path='/',expires=e)
	    resp.setCookie('dtpref_cols',str(cols),path='/',expires=e)
	    return self.manage_editForm(self,REQUEST,title=title,__str__=data,
				        acl_type=acl_type,acl_roles=acl_roles,
					dtpref_cols=cols,dtpref_rows=rows)
        if SUBMIT=='Bigger':
            rows=atoi(dtpref_rows)+5
            cols=atoi(dtpref_cols)+5
	    e='Friday, 31-Dec-99 23:59:59 GMT'
	    resp=REQUEST['RESPONSE']
	    resp.setCookie('dtpref_rows',str(rows),path='/',expires=e)
	    resp.setCookie('dtpref_cols',str(cols),path='/',expires=e)
	    return self.manage_editForm(self,REQUEST,title=title,__str__=data,
				        acl_type=acl_type,acl_roles=acl_roles,
					dtpref_cols=cols,dtpref_rows=rows)
	if SUBMIT=='Cancel':
	    return MessageDialog(title='Changes Cancelled',
	                         message='Your changes have been discarded',
	                         action='%s/manage_main' % REQUEST['URL2'])

	self.title=title
	self._setRoles(acl_type,acl_roles)
	self.munge(data)
	if REQUEST: return self.manage_editedDialog(REQUEST)

default_html="""<!--#var standard_html_header-->
<H2><!--#var title_or_id--> <!--#var document_title--></H2>
<P>This is the <!--#var document_id--> Document in 
the <!--#var title_and_id--> Folder.</P>
<!--#var standard_html_footer-->"""


class DocumentHandler:
    """Document object handler mixin"""
    meta_types=({'name':'Document', 'action':'manage_addDocumentForm'},)

    manage_addDocumentForm=HTMLFile('OFS/documentAdd')

    def manage_addDocument(self,id,title='',file='',
			   acl_type='A',acl_roles=[],REQUEST=None):
	"""Add a new Document object"""
	if not file: file=default_html
        i=Document(file, __name__=id)
	i.title=title
	i._setRoles(acl_type,acl_roles)
	self._setObject(id,i)
	if REQUEST: return self.manage_main(self,REQUEST)

    def documentIds(self):
	t=[]
	for i in self.objectMap():
	    if i['meta_type']=='Document':
		t.append(i['id'])
	return t

    def documentValues(self):
	t=[]
	for i in self.objectMap():
	    if i['meta_type']=='Document':
		t.append(getattr(self,i['id']))
	return t

    def documentItems(self):
	t=[]
	for i in self.objectMap():
	    if i['meta_type']=='Document':
		n=i['id']
		t.append((n,getattr(self,n)))
	return t



def decapitate(html, RESPONSE=None,
	       header_re=regex.compile(
		   '\(\('
		   	  '[^\0- <>:]+:[^\n]*\n'
		      '\|'
		   	  '[ \t]+[^\0- ][^\n]*\n'
		   '\)+\)[ \t]*\n\([\0-\377]+\)'
		   ),
	       space_re=regex.compile('\([ \t]+\)'),
	       name_re=regex.compile('\([^\0- <>:]+\):\([^\n]*\)'),
	       ):
    if header_re.match(html) < 0: return html

    headers, html = header_re.group(1,3)

    headers=split(headers,'\n')

    i=1
    while i < len(headers):
	if not headers[i]:
	    del headers[i]
	elif space_re.match(headers[i]) >= 0:
	    headers[i-1]="%s %s" % (headers[i-1],
				    headers[i][len(space_re.group(1)):])
	    del headers[i]
	else:
	    i=i+1

    for i in range(len(headers)):
	if name_re.match(headers[i]) >= 0:
	    k, v = name_re.group(1,2)
	    v=strip(v)
	else:
	    raise ValueError, 'Invalid Header (%d): %s ' % (i,headers[i])
	RESPONSE.setHeader(k,v)

    return html

