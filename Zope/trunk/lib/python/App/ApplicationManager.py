
__doc__="""Application management component"""
__version__='$Revision: 1.8 $'[11:-2]


import sys,os,time,Globals
from Acquisition import Acquirer
from Management import Management
from Globals import HTMLFile
from CacheManager import CacheManager

class ApplicationManager(Acquirer,Management,CacheManager):
    """Application management component."""

    manage_main    =HTMLFile('App/appMain')
    manage_packForm=HTMLFile('App/pack')
    manage_undoForm=HTMLFile('App/undo')

    manage_options=(
    {'icon':'App/arrow.jpg', 'label':'Application',
     'action':'manage_app',   'target':'_top'},
    {'icon':'App/arrow.jpg', 'label':'Application Manager',
     'action':'manage_main',   'target':'manage_main'},
    {'icon':'App/arrow.jpg', 'label':'Cache Manager',
     'action':'manage_cacheForm',   'target':'manage_main'},
    )
    name=title   ='Control Panel'
    process_id   =os.getpid()
    process_start=int(time.time())

    def manage_app(self, URL2):
	"""Return to the main management screen"""
	raise 'Redirect', URL2+'/manage'

    def parentObject(self):
	try:    return (self.aq_parent,)
	except: return ()

    def process_time(self):
        s=int(time.time())-self.process_start   
        d=int(s/86400)
        s=s-(d*86400)
        h=int(s/3600)
        m=int((s-(h*3600))/60)
        d=d and ('%s day%s'  % (d,(d!=1 and 's' or ''))) or ''
        return '%s %02d:%02d' % (d,h,m)

    def db(self):      return Globals.Bobobase

    def db_name(self): return Globals.BobobaseName

    def db_size(self):
        s=os.stat(self.db_name())[6]
	if s >= 1048576.0: return '%.1fM' % (s/1048576.0)
        return '%.1fK' % (s/1024.0)

    def manage_shutdown(self):
        """Shut down the application"""
	db=Globals.Bobobase._jar.db
	db.save_index()
	db.file.close()
	sys.exit(0)

    def manage_pack(self, days=0, REQUEST):
	"""Pack the database"""
	Globals.Bobobase._jar.db.pack(time.time()-days*86400,1)
	return self.manage_main(self, REQUEST)

    def revert_points(self): return ()

    def manage_addProduct(self, product):
	"""Register a product
	"""
	products=Globals.Bobobase['products']
	if product not in products:
	    Globals.Bobobase['products']=tuple(products)+(product,)
