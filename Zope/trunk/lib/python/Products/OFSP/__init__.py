############################################################################## 
#
#     Copyright 
#
#       Copyright 1997 Digital Creations, L.C., 910 Princess Anne
#       Street, Suite 300, Fredericksburg, Virginia 22401 U.S.A. All
#       rights reserved.
#
############################################################################## 
__doc__='''OFS
$Id: __init__.py,v 1.10 1998/02/13 21:03:48 jim Exp $'''
__version__='$Revision: 1.10 $'[11:-2]

import Session, DraftFolder
from ImageFile import ImageFile
import OFS.Image, OFS.Document

classes=('Session.Session', 'OFS.Image.File', 
	 'OFS.Image.Image', 'OFS.Document.Document')

meta_types=(
#    {'name':'Draft Folder', 'action':'manage_addDraftFolderForm'},
    {'name':'User Folder', 'action':'manage_addUserFolder'},
    {'name':'Session', 'action':'manage_addSessionForm'},
    {'name':'File', 'action':'manage_addFileForm'},
    {'name':'Image', 'action':'manage_addImageForm'},
    {'name':'Folder', 'action':'manage_addFolderForm'},
    {'name':'Document', 'action':'manage_addDocumentForm'},
    )

methods={
    'manage_addSessionForm': Session.manage_addSessionForm,
    'manage_addSession': Session.manage_addSession,
#    'manage_addDraftFolderForm': DraftFolder.addForm,
#    'manage_addDraftFolder': DraftFolder.add,
    }

misc_={
    'draft': ImageFile('images/DraftFolder.gif', globals()),
    'sup': ImageFile('images/DraftFolderControl.gif', globals()),
    'session': ImageFile('images/session.gif', globals()),
    }

__ac_permissions__=(
    ('Add Sessions',('manage_addSessionForm', 'manage_addSession')),
    #('Add DraftFolders',
    # ('manage_addDraftFolderForm', 'manage_addDraftFolder')),
    )

############################################################################## 
#
# $Log: __init__.py,v $
# Revision 1.10  1998/02/13 21:03:48  jim
# Rearranged meta_types so Document shows up first.
#
# Revision 1.9  1998/02/10 18:41:40  jim
# Changed session creation method names for latest security scheme.
#
# Added User Folder.
#
# Added permissions info for sessions.
#
# Revision 1.8  1998/02/09 17:25:41  jim
# *** empty log message ***
#
# Revision 1.7  1998/01/29 20:52:00  brian
# Added eval support
#
# Revision 1.6  1998/01/29 20:21:57  brian
# Added eval support
#
# Revision 1.5  1998/01/15 15:05:22  brian
# Fixed setup and removed DraftFolders from 1.0 release
#
# Revision 1.4  1997/12/31 17:21:27  brian
# *** empty log message ***
#
# Revision 1.3  1997/12/19 19:14:15  jim
# updated icon management strategy
#
# Revision 1.2  1997/12/19 17:06:22  jim
# moved Sessions and Daft folders here.
#
# Revision 1.1  1997/12/18 17:05:54  jim
# *** empty log message ***
#
# Revision 1.3  1997/11/11 19:26:37  jim
# Added DraftFolder.
#
# Revision 1.2  1997/11/10 16:32:54  jim
# Changed to support separate Image and File objects.
#
# Revision 1.1  1997/11/07 19:31:42  jim
# *** empty log message ***
#
# Revision 1.1  1997/10/09 17:34:53  jim
# first cut, no testing
#
# Revision 1.1  1997/07/25 18:14:28  jim
# initial
#
#
