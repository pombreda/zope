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
__doc__='''Base Principia
$Id: __init__.py,v 1.20 1999/03/08 21:25:02 michel Exp $'''
__version__='$Revision: 1.20 $'[11:-2]

import Version, Draft, ZClasses
import OFS.Image, OFS.Folder, AccessControl.User
import OFS.DTMLMethod, OFS.DTMLDocument
from ImageFile import ImageFile

product_name='Zope built-in objects'

classes=('OFS.DTMLMethod.DTMLMethod', 'OFS.DTMLDocument.DTMLDocument',
         'Version.Version', 'OFS.Image.File', 'OFS.Image.Image',
         )
klasses=('OFS.Folder.Folder', 'AccessControl.User.UserFolder')

meta_types=(
    ZClasses.meta_types+
    (
        {'name': Draft.Draft.meta_type,
         'action':'manage_addPrincipiaDraftForm'},
        {'name': 'User Folder',
         'action':'manage_addUserFolder'},
        {'name': 'Version',
         'action':'manage_addVersionForm'},
        {'name': 'File',
         'action':'manage_addFileForm'},
        {'name': 'Image',
         'action':'manage_addImageForm'},
        {'name': 'Folder',
         'action':'manage_addFolderForm'},
        {'name': 'DTML Method',
         'action':'manage_addDTMLMethodForm'},
        {'name': 'DTML Document',
         'action':'manage_addDTMLDocumentForm'},
        )
    )

def PUT(self):
    # This is here mainly as a hac^H^Hook for holding PUT permissions
    raise TypeError, 'Directory PUT is not supported'

methods={
    # for bw compatibility
    'manage_addDocument': OFS.DTMLMethod.add,    
    'manage_addDTMLMethod': OFS.DTMLMethod.add,
    'manage_addDTMLMethodForm': OFS.DTMLMethod.addForm,
    'manage_addDTMLDocument': OFS.DTMLDocument.add,
    'manage_addDTMLDocumentForm': OFS.DTMLDocument.addForm,
    'manage_addFolder': OFS.Folder.manage_addFolder,
    'manage_addFolderForm': OFS.Folder.manage_addFolderForm,
    'manage_addImage': OFS.Image.manage_addImage,
    'manage_addImageForm': OFS.Image.manage_addImageForm,
    'manage_addFile': OFS.Image.manage_addFile,
    'manage_addFileForm': OFS.Image.manage_addFileForm,
    'manage_addVersionForm': Version.manage_addVersionForm,
    'manage_addVersion': Version.manage_addVersion,
    'PUT': PUT,
    'PUT__roles__': ('Manager',),
    'manage_addUserFolder': AccessControl.User.manage_addUserFolder,
    'manage_addPrincipiaDraftForm': Draft.manage_addPrincipiaDraftForm,
    'manage_addPrincipiaDraft': Draft.manage_addPrincipiaDraft,
    }
methods.update(ZClasses.methods)

misc_={
    'version': ImageFile('images/version.gif', globals()),
    }
misc_.update(ZClasses.misc_)

__ac_permissions__=(
    ZClasses.__ac_permissions__+
    (
        ('Add Versions',('manage_addVersionForm', 'manage_addVersion')),
        ('Add Documents, Images, and Files',
         ('manage_addDTMLDocumentForm', 'manage_addDTMLDocument',
          'manage_addDTMLMethodForm', 'manage_addDTMLMethod',
          'manage_addFileForm', 'manage_addFile',
          'manage_addImageForm', 'manage_addImage',
          'PUT')
         ),
        ('Add Folders',('manage_addFolderForm', 'manage_addFolder')),
        ('Add User Folders',('manage_addUserFolder',)),
        ('Change DTML Documents', ()),
        ('Change DTML Methods', ()),
        ('Change Images and Files', ()),
        ('Change proxy roles', ()),
        ('Change Versions', ()),
        ('Join/leave Versions', ()),
        ('Save/discard Version changes', ()),
        ('Manage users', ()),
        #('Add DraftFolders',
        # ('manage_addDraftFolderForm', 'manage_addDraftFolder')),
        )
    )
