##############################################################################
#
# Zope Public License (ZPL) Version 0.9.4
# ---------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
# 
# 1. Redistributions in source code must retain the above
#    copyright notice, this list of conditions, and the following
#    disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions, and the following
#    disclaimer in the documentation and/or other materials
#    provided with the distribution.
# 
# 3. Any use, including use of the Zope software to operate a
#    website, must either comply with the terms described below
#    under "Attribution" or alternatively secure a separate
#    license from Digital Creations.
# 
# 4. All advertising materials, documentation, or technical papers
#    mentioning features derived from or use of this software must
#    display the following acknowledgement:
# 
#      "This product includes software developed by Digital
#      Creations for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
# 5. Names associated with Zope or Digital Creations must not be
#    used to endorse or promote products derived from this
#    software without prior written permission from Digital
#    Creations.
# 
# 6. Redistributions of any form whatsoever must retain the
#    following acknowledgment:
# 
#      "This product includes software developed by Digital
#      Creations for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
# 7. Modifications are encouraged but must be packaged separately
#    as patches to official Zope releases.  Distributions that do
#    not clearly separate the patches from the original work must
#    be clearly labeled as unofficial distributions.
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND
#   ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
#   FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT
#   SHALL DIGITAL CREATIONS OR ITS CONTRIBUTORS BE LIABLE FOR ANY
#   DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#   CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#   DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#   LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
#   IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
#   THE POSSIBILITY OF SUCH DAMAGE.
# 
# Attribution
# 
#   Individuals or organizations using this software as a web site
#   must provide attribution by placing the accompanying "button"
#   and a link to the accompanying "credits page" on the website's
#   main entry point.  In cases where this placement of
#   attribution is not feasible, a separate arrangment must be
#   concluded with Digital Creations.  Those using the software
#   for purposes other than web sites must provide a corresponding
#   attribution in locations that include a copyright using a
#   manner best suited to the application environment.
# 
# This software consists of contributions made by Digital
# Creations and many individuals on behalf of Digital Creations.
# Specific attributions are listed in the accompanying credits
# file.
# 
##############################################################################
"""Principia Product Objects
"""
# The new Product model:
# 
#   Products may be defined with Principia or by placing directories in
#   lib/python/Products.
# 
#   Products in lib/python/Products may have up to three sources of information:
# 
#       - Static information defined via Python.  This information is
#         described and made available via __init__.py.
# 
#       - Dynamic object data that gets copied into the Bobobase.
#         This is contained in product.dat (which is obfuscated).
# 
#       - Static extensions supporting the dynamic data.  These too
#         are obfuscated.
# 
#   Products may be copied and pasted only within the products folder.
# 
#   If a product is deleted (or cut), it is automatically recreated
#   on restart if there is still a product directory.


import Globals, OFS.Folder, OFS.SimpleItem, os, string, Acquisition
from OFS.Folder import Folder
import regex, zlib, Globals, cPickle, marshal, Main, rotor
from string import rfind, atoi, find, strip, join
from Factory import Factory

class ProductFolder(Folder):
    "Manage a collection of Products"

    id        ='Products'
    name=title='Product Management'
    meta_type ='Product Management'
    icon='p_/ProductFolder_icon'

    manage_options=(
    {'label':'Contents', 'action':'manage_main'},
    {'label':'Properties', 'action':'manage_propertiesForm'},
    {'label':'Security', 'action':'manage_access'},
    {'label':'Undo', 'action':'manage_UndoForm'},
    {'label':'Find', 'action':'manage_findFrame'},
    )

    all_meta_types={'name': 'Product', 'action': 'manage_addProductForm'},
    meta_types=all_meta_types

    def _product(self, name): return getattr(self, name)

    manage_addProductForm=Globals.HTMLFile('addProduct',globals())
    def manage_addProduct(self, id, title, REQUEST=None):
        ' '
        i=Product(id, title)
        self._setObject(id,i)
        if REQUEST is not None:
            return self.manage_main(self,REQUEST,update_menu=1)

    def _delObject(self,id):
        for factory in getattr(self, id)._factories(): factory._unregister()
        ProductFolder.inheritedAttribute('_delObject')(self, id)

    def _canCopy(self, op=0):
        return 0

class Product(Folder):
    """Model a product that can be created through the web.
    """
    meta_type='Product'
    icon='p_/Product_icon'
    version=''
    configurable_objects_=()
    import_error_=None

    def new_version(self,
                    _intending=regex.compile("[.]?[0-9]+$").search,
                    ):
        # Return a new version number based on the existing version.
        v=str(self.version)
        if not v: return '1.0'
        if _intending(v) < 0: return v
        l=rfind(v,'.')
        return v[:l+1]+str(1+atoi(v[l+1:]))            
                    
    
    meta_types=(
        {
            'name': 'Principia Factory',
            'action': 'manage_addPrincipiaFactoryForm'
            },
        )

    manage_options=(
    {'label':'Contents', 'action':'manage_main'},
    {'label':'Properties', 'action':'manage_propertiesForm'},
    {'label':'Security', 'action':'manage_access'},
    {'label':'Undo', 'action':'manage_UndoForm'},
    {'label':'Find', 'action':'manage_findFrame'},
    {'label':'Distribution', 'action':'manage_distributionView'},
    )

    manage_distributionView=Globals.HTMLFile('distributionView',globals())

    _properties=Folder._properties+(
        {'id':'version', 'type': 'string'},
        )

    manage_addPrincipiaFactoryForm=Globals.HTMLFile('addFactory',globals())
    def manage_addPrincipiaFactory(
        self, id, title, object_type, initial, REQUEST=None):
        ' '
        i=Factory(id, title, object_type, initial, self)
        self._setObject(id,i)
        if REQUEST is not None:
            return self.manage_main(self,REQUEST,update_menu=1)

    def _delObject(self,id):
        o=getattr(self, id)
        if o.meta_type==Factory.meta_type: o._unregister()
        Product.inheritedAttribute('_delObject')(self, id)
        
    def __init__(self, id, title):
        self.id=id
        self.title=title

    def _notifyOfCopyTo(self, container, op=0):
        if container.__class__ is not ProductFolder:
            raise TypeError, (
                'Products can only be copied to <b>product folders</b>.')

    def _postCopy(self, container, op=0):
        for factory in self._factories():
            factory._register()

    def _factories(self):
        r=[]
        append=r.append
        for o in self.__dict__.values():
            if hasattr(o,'meta_type') and o.meta_type==Factory.meta_type:
                append(o.__of__(self))

        return r
        

    def Destination(self):
        "Return the destination for factory output"
        return self
    Destination__roles__=None

    def DestinationURL(self):
        "Return the URL for the destination for factory output"
        return self.REQUEST['BASE4']
    DestinationURL__roles__=None

    def manage_distribute(self, version, RESPONSE, configurable_objects=[]):
        "Set the product up to create a distribution and give a link"
        if self.__dict__.has_key('manage_options'):
            raise TypeError, 'This product is <b>not</b> redistributable.'
        self.version=version=strip(version)
        self.configurable_objects_=configurable_objects
        RESPONSE.redirect('Distributions/%s-%s.tar.gz' % (self.id, version))
        
    def _distribution(self):
        # Return a distribution
        if self.__dict__.has_key('manage_options'):
            raise TypeError, 'This product is <b>not</b> redistributable.'

        id=self.id
        
        import tar
        rot=rotor.newrotor(id+' shshsh')
        ar=tar.tgzarchive("%s-%s" % (id, self.version))
        prefix="lib/python/Products/%s/" % self.id

        # __init__.py
        ar.add(prefix+"__init__.py",
               '''"Product %s"
               ''' % id
               )

        # Extensions
        pp=id+'.'
        lpp=len(pp)
        ed=os.path.join(INSTANCE_HOME,'Extensions')
        if os.path.exists(ed):
            for name in os.listdir(ed):
                suffix=''
                if name[:lpp]==pp:
                    path=os.path.join(ed, name)
                    try:
                        f=open(path)
                        data=f.read()
                        f.close()
                        if name[-3:]=='.py':
                            data=rot.encrypt(zlib.compress(data))
                            suffix='p'
                    except: data=None
                    if data:
                        ar.add("%sExtensions/%s%s" %
                               (prefix,name[lpp:],suffix),
                               data)

        # version.txt
        ar.add(prefix+'version.txt', self.version)

        # product.dat
        f=CompressedOutputFile(rot)
        meta={
            '_objects': tuple(filter(
            lambda o, obs=self.configurable_objects_:
            o['id'] in obs,
            self._objects))
            }
        f.write(cPickle.dumps(meta,1))
        self._p_jar.db.exportoid(self._p_oid, f)
        ar.add(prefix+'product.dat', f.getdata())

        ar.finish()
        return str(ar)

    class Distributions(Acquisition.Explicit):
        "Product Distributions"

        def __bobo_traverse__(self, REQUEST, name):
            if name[-7:] != '.tar.gz': raise 'Invalid Name', name
            l=find(name,'-')
            id, version = name[:l], name[l+1:-7]
            product=self.aq_parent
            if product.id==id and product.version==version:
                return Distribution(product)

            raise 'Invalid version or product id', name

    Distributions=Distributions()

    manage_traceback=Globals.HTMLFile('traceback',globals())
    manage_readme=Globals.HTMLFile('readme',globals())
    def manage_get_product_readme__(self):
        try:
            return open(os.path.join(
                SOFTWARE_HOME, 'Products', self.id,'README.txt'
                )).read()
        except: return ''


class CompressedOutputFile:
    def __init__(self, rot):
        self._c=zlib.compressobj()
        self._r=[]
        self._rot=rot
        rot.encrypt('')

    def write(self, s):
        self._r.append(self._rot.encryptmore(self._c.compress(s)))

    def getdata(self):
        self._r.append(self._rot.encryptmore(self._c.flush()))
        return join(self._r,'')

class CompressedInputFile:
    _done=0
    def __init__(self, f, rot):
        self._c=zlib.decompressobj()
        self._b=''
        if type(rot) is type(''): rot=rotor.newrotor(rot)
        self._rot=rot
        rot.decrypt('')
        self._f=f

    def _next(self):
        if self._done: return
        l=self._f.read(8196)
        if not l:
            l=self._c.flush()
            self._done=1
        else:
            l=self._c.decompress(self._rot.decryptmore(l))
        self._b=self._b+l

    def read(self, l=None):
        if l is None:
            while not self._done: self._next()
            l=len(self._b)
        else:
            while l > len(self._b) and not self._done: self._next()
        r=self._b[:l]
        self._b=self._b[l:]

        return r

    def readline(self):
        l=find(self._b, '\n')
        while l < 0 and not self._done:
            self._next()
            l=find(self._b, '\n')
        if l < 0: l=len(self._b)
        else: l=l+1
        r=self._b[:l]
        self._b=self._b[l:]
        return r

class Distribution:
    "A distribution builder"
    
    def __init__(self, product):
        self._product=product

    def index_html(self, RESPONSE):
        "Return distribution data"
        r=self._product._distribution()
        RESPONSE['content-type']='application/x-gzip'
        return r

def initializeProduct(productp, name, home, app):
    # Initialize a levered product

    products=app.Control_Panel.Products

    if hasattr(productp, 'import_error_'): ie=productp.import_error_
    else: ie=None

    try: fver=strip(open(home+'/version.txt').read())
    except: fver=''
    old=None
    try:
        if ihasattr(products,name):
            old=getattr(products, name)
            if (ihasattr(old,'version') and old.version==fver and
                hasattr(old, 'import_error_') and
                old.import_error_==ie):
                return
    except: pass
    
    try:
        f=CompressedInputFile(open(home+'/product.dat'),name+' shshsh')
        meta=cPickle.Unpickler(f).load()
        product=Globals.Bobobase._jar.import_file(f)
        product._objects=meta['_objects']
    except:
        f=fver and (" (%s)" % fver)
        product=Product(name, 'Installed product %s%s' % (name,f))

    if old is not None: products._delObject(name)
    products._setObject(name, product)
    product.__of__(products)._postCopy(products)
    product.manage_options=Folder.manage_options
    product.icon='p_/InstalledProduct_icon'
    product.version=fver
    product._distribution=None
    product.manage_distribution=None
    product.thisIsAnInstalledProduct=1

    if ie:
        product.import_error_=ie
        product.title='Broken product %s' % name
        product.icon='p_/BrokenProduct_icon'
        product.manage_options=(
            {'label':'Traceback', 'action':'manage_traceback'},
            )

    if os.path.exists(os.path.join(home, 'README.txt')):
        product.manage_options=product.manage_options+(
            {'label':'README', 'action':'manage_readme'},
            )
        

def ihasattr(o, name):
    return hasattr(o, name) and o.__dict__.has_key(name)
