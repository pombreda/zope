##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
"""Access control package"""

__version__='$Revision: 1.160 $'[11:-2]

import Globals, socket, SpecialUsers,re
import os
from Globals import DTMLFile, MessageDialog, Persistent, PersistentMapping
from string import join, strip, split, lower, upper
from App.Management import Navigation, Tabs
from Acquisition import Implicit
from OFS.SimpleItem import Item
from base64 import decodestring
from App.ImageFile import ImageFile
from Role import RoleManager, DEFAULTMAXLISTUSERS
from PermissionRole import _what_not_even_god_should_do, rolesForPermissionOn
import AuthEncoding
from AccessControl import getSecurityManager
from zExceptions import Unauthorized
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.ZopeSecurityPolicy import _noroles

ListType=type([])
NotImplemented='NotImplemented'

_marker=[]

class BasicUser(Implicit):
    """Base class for all User objects"""

    # ----------------------------
    # Public User object interface
    # ----------------------------
    
    # Maybe allow access to unprotected attributes. Note that this is
    # temporary to avoid exposing information but without breaking
    # everyone's current code. In the future the security will be
    # clamped down and permission-protected here. Because there are a
    # fair number of user object types out there, this method denies
    # access to names that are private parts of the standard User
    # interface or implementation only. The other approach (only
    # allowing access to public names in the User interface) would
    # probably break a lot of other User implementations with extended
    # functionality that we cant anticipate from the base scaffolding.
    def __allow_access_to_unprotected_subobjects__(self, name, value=None):
        deny_names=('name', '__', 'roles', 'domains', '_getPassword',
                    'authenticate', '_shared_roles')
        if name in deny_names:
            return 0
        return 1
        
    def __init__(self,name,password,roles,domains):
        raise NotImplemented

    def getUserName(self):
        """Return the username of a user"""
        raise NotImplemented

    def getId(self):
        """Get the ID of the user. The ID can be used, at least from
        Python, to get the user from the user's
        UserDatabase"""
        return self.getUserName()        

    def _getPassword(self):
        """Return the password of the user."""
        raise NotImplemented

    def getRoles(self):
        """Return the list of roles assigned to a user."""
        raise NotImplemented

    def getRolesInContext(self, object):
        """Return the list of roles assigned to the user,
           including local roles assigned in context of
           the passed in object."""
        name=self.getUserName()
        roles=self.getRoles()
        local={}
        object=getattr(object, 'aq_inner', object)
        while 1:
            local_roles = getattr(object, '__ac_local_roles__', None)
            if local_roles:
                if callable(local_roles):
                    local_roles=local_roles()
                dict=local_roles or {}
                for r in dict.get(name, []):
                    local[r]=1
            inner = getattr(object, 'aq_inner', object)
            parent = getattr(inner, 'aq_parent', None)
            if parent is not None:
                object = parent
                continue
            if hasattr(object, 'im_self'):
                object=object.im_self
                object=getattr(object, 'aq_inner', object)
                continue
            break
        roles=list(roles) + local.keys()
        return roles

    def getDomains(self):
        """Return the list of domain restrictions for a user"""
        raise NotImplemented

    # ------------------------------
    # Internal User object interface
    # ------------------------------
    
    def authenticate(self, password, request):
        passwrd=self._getPassword()
        result = AuthEncoding.pw_validate(passwrd, password)
        domains=self.getDomains()
        if domains:
            return result and domainSpecMatch(domains, request)
        return result

    
    def _shared_roles(self, parent):
          r=[]
          while 1:
              if hasattr(parent,'__roles__'):
                  roles=parent.__roles__
                  if roles is None: return 'Anonymous',
                  if 'Shared' in roles:
                      roles=list(roles)
                      roles.remove('Shared')
                      r=r+roles
                  else:
                      try: return r+list(roles)
                      except: return r
              if hasattr(parent, 'aq_parent'):
                  while hasattr(parent.aq_self,'aq_self'):
                      parent=parent.aq_self
                  parent=parent.aq_parent
              else: return r

    def _check_context(self, object):
        # Check that 'object' exists in the acquisition context of
        # the parent of the acl_users object containing this user,
        # to prevent "stealing" access through acquisition tricks.
        # Return true if in context, false if not or if context
        # cannot be determined (object is not wrapped).
        parent  = getattr(self, 'aq_parent', None)
        context = getattr(parent, 'aq_parent', None)
        if context is not None:
            if object is None:
                return 1
            if not hasattr(object, 'aq_inContextOf'):
                if hasattr(object, 'im_self'):
                    # This is a method.  Grab its self.
                    object=object.im_self
                if not hasattr(object, 'aq_inContextOf'):
                    # Object is not wrapped, so return false.
                    return 0
            return object.aq_inContextOf(context, 1)

        # This is lame, but required to keep existing behavior.
        return 1

    def allowed(self, object, object_roles=None):
        """Check whether the user has access to object. The user must
           have one of the roles in object_roles to allow access."""

        if object_roles is _what_not_even_god_should_do: return 0

        # Short-circuit the common case of anonymous access.
        if object_roles is None or 'Anonymous' in object_roles:
            return 1

        # Provide short-cut access if object is protected by 'Authenticated'
        # role and user is not nobody
        if 'Authenticated' in object_roles and (
            self.getUserName() != 'Anonymous User'):
            return 1

        # Check for ancient role data up front, convert if found.
        # This should almost never happen, and should probably be
        # deprecated at some point.
        if 'Shared' in object_roles:
            object_roles = self._shared_roles(object)
            if object_roles is None or 'Anonymous' in object_roles:
                return 1

        # Check for a role match with the normal roles given to
        # the user, then with local roles only if necessary. We
        # want to avoid as much overhead as possible.
        user_roles = self.getRoles()
        for role in object_roles:
            if role in user_roles:
                if self._check_context(object):
                    return 1
                return None

        # Still have not found a match, so check local roles. We do
        # this manually rather than call getRolesInContext so that
        # we can incur only the overhead required to find a match.
        inner_obj = getattr(object, 'aq_inner', object)
        user_name = self.getUserName()
        while 1:
            local_roles = getattr(inner_obj, '__ac_local_roles__', None)
            if local_roles:
                if callable(local_roles):
                    local_roles = local_roles()
                dict = local_roles or {}
                local_roles = dict.get(user_name, [])
                for role in object_roles:
                    if role in local_roles:
                        if self._check_context(object):
                            return 1
                        return 0
            inner = getattr(inner_obj, 'aq_inner', inner_obj)
            parent = getattr(inner, 'aq_parent', None)
            if parent is not None:
                inner_obj = parent
                continue
            if hasattr(inner_obj, 'im_self'):
                inner_obj=inner_obj.im_self
                inner_obj=getattr(inner_obj, 'aq_inner', inner_obj)
                continue
            break
        return None

    def hasRole(self, *args, **kw):
        """hasRole is an alias for 'allowed' and has been deprecated.
        
        Code still using this method should convert to either 'has_role' or
        'allowed', depending on the intended behaviour.

        """
        import warnings
        warnings.warn('BasicUser.hasRole is deprecated, please use '
            'BasicUser.allowed instead; hasRole was an alias for allowed, but '
            'you may have ment to use has_role.', DeprecationWarning)
        self.allowed(*args, **kw)

    domains=[]
    
    def has_role(self, roles, object=None):
        """Check to see if a user has a given role or roles."""
        if type(roles)==type('s'):
            roles=[roles]
        if object is not None:
            user_roles = self.getRolesInContext(object)
        else:
            # Global roles only...
            user_roles=self.getRoles()
        for role in roles:
            if role in user_roles:
                return 1
        return 0

    def has_permission(self, permission, object):
        """Check to see if a user has a given permission on an object."""
        return getSecurityManager().checkPermission(permission, object)

    def __len__(self): return 1
    def __str__(self): return self.getUserName()
    __repr__=__str__


class SimpleUser(BasicUser):
    """A very simple user implementation

    that doesn't make a database commitment"""

    def __init__(self,name,password,roles,domains):
        self.name   =name
        self.__     =password
        self.roles  =roles
        self.domains=domains

    def getUserName(self):
        """Return the username of a user"""
        return self.name

    def _getPassword(self):
        """Return the password of the user."""
        return self.__

    def getRoles(self):
        """Return the list of roles assigned to a user."""
        if self.name == 'Anonymous User': return tuple(self.roles)
        else: return tuple(self.roles) + ('Authenticated',)

    def getDomains(self):
        """Return the list of domain restrictions for a user"""
        return tuple(self.domains)

class SpecialUser(SimpleUser):
    """Class for special users, like emergency user and nobody"""
    def getId(self): pass

class User(SimpleUser, Persistent):
    """Standard User object"""

class UnrestrictedUser(SpecialUser):
    """User that passes all security checks.  Note, however, that modules
    like Owner.py can still impose restrictions.
    """
    def allowed(self,parent,roles=None):
        return roles is not _what_not_even_god_should_do

    def hasRole(self, *args, **kw):
        """hasRole is an alias for 'allowed' and has been deprecated.
        
        Code still using this method should convert to either 'has_role' or
        'allowed', depending on the intended behaviour.

        """
        import warnings
        warnings.warn('UnrestrictedUser.hasRole is deprecated, please use '
            'UnrestrictedUser.allowed instead; hasRole was an alias for '
            'allowed, but you may have ment to use has_role.',
            DeprecationWarning)
        self.allowed(*args, **kw)

    def has_role(self, roles, object=None): return 1

    def has_permission(self, permission, object): return 1


class NullUnrestrictedUser(SpecialUser):
    """User created if no emergency user exists. It is only around to
       satisfy third party userfolder implementations that may
       expect the emergency user to exist and to be able to call certain
       methods on it (in other words, backward compatibility).

       Note that when no emergency user is installed, this object that
       exists in its place is more of an anti-superuser since you cannot
       login as this user and it has no priveleges at all."""

    __null_user__=1

    def __init__(self):
        pass

    def getUserName(self):
        # return an unspellable username
        return (None, None)
    _getPassword=getUserName

    def getRoles(self):
        return ()
    getDomains=getRoles

    def getRolesInContext(self, object):
        return ()

    def authenticate(self, password, request):
        return 0

    def allowed(self, parent, roles=None):
        return 0

    def hasRole(self, *args, **kw):
        """hasRole is an alias for 'allowed' and has been deprecated.
        
        Code still using this method should convert to either 'has_role' or
        'allowed', depending on the intended behaviour.

        """
        import warnings
        warnings.warn('NullUnrestrictedUser.hasRole is deprecated, please use '
            'NullUnrestrictedUser.allowed instead; hasRole was an alias for '
            'allowed, but you may have ment to use has_role.',
            DeprecationWarning)
        self.allowed(*args, **kw)

    def has_role(self, roles, object=None):
        return 0

    def has_permission(self, permission, object):
        return 0

    

def readUserAccessFile(filename):
    '''Reads an access file from INSTANCE_HOME.
    Returns name, password, domains, remote_user_mode.
    '''
    try:
        f = open(os.path.join(INSTANCE_HOME, filename), 'r')
        line = f.readline()
        f.close()
    except IOError:
        return None

    if line:
        data = split(strip(line), ':')
        remote_user_mode = not data[1]
        try:    ds = split(data[2], ' ')
        except: ds = []
        return data[0], data[1], ds, remote_user_mode
    else:
        return None


# Create emergency user.
_remote_user_mode=0

info = readUserAccessFile('access')
if info:
    _remote_user_mode = info[3]
    emergency_user = UnrestrictedUser(
        info[0], info[1], ('manage',), info[2])
else:
    emergency_user = NullUnrestrictedUser()

super = emergency_user  # Note: use of the 'super' name is deprecated.
del info


nobody=SpecialUser('Anonymous User','',('Anonymous',), [])
system=UnrestrictedUser('System Processes','',('manage',), [])

# stuff these in a handier place for importing
SpecialUsers.nobody=nobody
SpecialUsers.system=system
SpecialUsers.emergency_user=emergency_user
# Note: use of the 'super' name is deprecated.
SpecialUsers.super=emergency_user


class BasicUserFolder(Implicit, Persistent, Navigation, Tabs, RoleManager,
                      Item):
    """Base class for UserFolder-like objects"""

    meta_type='User Folder'
    id       ='acl_users'
    title    ='User Folder'

    isPrincipiaFolderish=1
    isAUserFolder=1
    maxlistusers = DEFAULTMAXLISTUSERS

    encrypt_passwords = 0

    manage_options=(
        (
        {'label':'Contents', 'action':'manage_main',
         'help':('OFSP','User-Folder_Contents.stx')},
        {'label':'Properties', 'action':'manage_userFolderProperties',
         'help':('OFSP','User-Folder_Properties.stx')},
        )
        +RoleManager.manage_options
        +Item.manage_options
        )

    __ac_permissions__=(
        ('Manage users',
         ('manage_users','getUserNames', 'getUser', 'getUsers',
          'getUserById', 'user_names', 'setDomainAuthenticationMode',
          'manage_addUser', 'manage_editUser', 'manage_delUsers',
          )
         ),
        )


    # ----------------------------------
    # Public UserFolder object interface
    # ----------------------------------
    
    def getUserNames(self):
        """Return a list of usernames"""
        raise NotImplemented

    def getUsers(self):
        """Return a list of user objects"""
        raise NotImplemented

    def getUser(self, name):
        """Return the named user object or None"""
        raise NotImplemented

    def getUserById(self, id, default=_marker):
        """Return the user corresponding to the given id.
        """
        try: return self.getUser(id)
        except:
           if default is _marker: raise
           return default

    # As of Zope 2.5, manage_addUser, manage_editUser and manage_delUsers
    # form the official API for user management. The old grotesque way of
    # using manage_users is now deprecated. Note that not all user folder
    # implementations support adding, changing and deleting user objects.

    # The default implementation of these API methods simply call the
    # _doXXX versions of the methods that user folder authors have already
    # implemented, which means that these APIs will work for current user
    # folder implementations without any action on the part of the author.

    # User folder authors that implement the new manage_XXX API can get
    # rid of the old _doXXX versions of the methods, which are no longer
    # required (we only use them if the new api is not directly implemented).

    def manage_addUser(self, name, password, roles, domains):
        """API method for creating a new user object. Note that not all
           user folder implementations support dynamic creation of user
           objects. Implementations that do not support dynamic creation
           of user objects should raise NotImplemented for this method."""
        if hasattr(self, '_doAddUser'):
            return self._doAddUser(name, password, roles, domains)
        raise NotImplemented

    def manage_editUser(self, name, password, roles, domains):
        """API method for changing user object attributes. Note that not
           all user folder implementations support changing of user object
           attributes. Implementations that do not support changing of user
           object attributes should raise NotImplemented for this method."""
        if hasattr(self, '_doChangeUser'):
            return self._doChangeUser(name, password, roles, domains)
        raise NotImplemented

    def manage_delUsers(self, names):
        """API method for deleting one or more user objects. Note that not
           all user folder implementations support deletion of user objects.
           Implementations that do not support deletion of user objects
           should raise NotImplemented for this method."""
        if hasattr(self, '_doDelUsers'):
            return self._doDelUsers(names)
        raise NotImplemented


    # -----------------------------------
    # Private UserFolder object interface
    # -----------------------------------

    _remote_user_mode=_remote_user_mode
    _domain_auth_mode=0
    _emergency_user=emergency_user
    # Note: use of the '_super' name is deprecated.
    _super=emergency_user
    _nobody=nobody


    def identify(self, auth):
        if auth and lower(auth[:6])=='basic ':
            try: name, password=tuple(split(decodestring(
                                      split(auth)[-1]), ':', 1))
            except:
                raise 'Bad Request', 'Invalid authentication token'
            return name, password
        else:
            return None, None

    def authenticate(self, name, password, request):
        emergency = self._emergency_user
        if name is None:
            return None
        if emergency and name==emergency.getUserName():
            user = emergency
        else:
            user = self.getUser(name)
        if user is not None and user.authenticate(password, request):
            return user
        else:
            return None

    def authorize(self, user, accessed, container, name, value, roles):
        user = getattr(user, 'aq_base', user).__of__(self)
        newSecurityManager(None, user)
        security = getSecurityManager()
        try:
            try:
                if security.validate(accessed, container, name, value, roles):
                    return 1
            except:
                noSecurityManager()
                raise
        except Unauthorized: pass
        return 0

    def validate(self, request, auth='', roles=_noroles):
        """
        this method performs identification, authentication, and
        authorization
        v is the object (value) we're validating access to
        n is the name used to access the object
        a is the object the object was accessed through
        c is the physical container of the object

        We allow the publishing machinery to defer to higher-level user
        folders or to raise an unauthorized by returning None from this
        method.
        """
        v = request['PUBLISHED'] # the published object
        a, c, n, v = self._getobcontext(v, request)

        # we need to continue to support this silly mode
        # where if there is no auth info, but if a user in our
        # database has no password and he has domain restrictions,
        # return him as the authorized user.
        if not auth:
            if self._domain_auth_mode:
                for user in self.getUsers():
                    if user.getDomains():
                        if self.authenticate(user.getUserName(), '', request):
                            if self.authorize(user, a, c, n, v, roles):
                                return user.__of__(self)

        name, password = self.identify(auth)
        user = self.authenticate(name, password, request)
        # user will be None if we can't authenticate him or if we can't find
        # his username in this user database.
        emergency = self._emergency_user
        if emergency and user is emergency:
            if self._isTop():
                # we do not need to authorize the emergency user against the
                # published object.
                return emergency.__of__(self)
            else:
                # we're not the top-level user folder
                return None
        elif user is None:
            # either we didn't find the username, or the user's password
            # was incorrect.  try to authorize and return the anonymous user.
            if self._isTop() and self.authorize(self._nobody, a,c,n,v,roles):
                return self._nobody.__of__(self)
            else:
                # anonymous can't authorize or we're not top-level user folder
                return None
        else:
            # We found a user, his password was correct, and the user
            # wasn't the emergency user.  We need to authorize the user
            # against the published object.
            if self.authorize(user, a, c, n, v, roles):
                return user.__of__(self)
            # That didn't work.  Try to authorize the anonymous user.
            elif self._isTop() and self.authorize(self._nobody,a,c,n,v,roles):
                return self._nobody.__of__(self)
            else:
                # we can't authorize the user, and we either can't authorize
                # nobody against the published object or we're not top-level
                return None
            
    if _remote_user_mode:
        
        def validate(self, request, auth='', roles=_noroles):
            v = request['PUBLISHED']
            a, c, n, v = self._getobcontext(v, request)
            name = request.environ.get('REMOTE_USER', None)
            if name is None:
                if self._domain_auth_mode:
                    for user in self.getUsers():
                        if user.getDomains():
                            if self.authenticate(
                                user.getUserName(), '', request
                                ):
                                if self.authorize(user, a, c, n, v, roles):
                                    return user.__of__(self)

            user = self.getUser(name)
            # user will be None if we can't find his username in this user
            # database.
            emergency = self._emergency_user
            if emergency and name==emergency.getUserName():
                if self._isTop():
                    # we do not need to authorize the emergency user against
                    #the published object.
                    return emergency.__of__(self)
                else:
                    # we're not the top-level user folder
                    return None
            elif user is None:
                # we didn't find the username in this database
                # try to authorize and return the anonymous user.
                if self._isTop() and self.authorize(self._nobody,
                                                    a, c, n, v, roles):
                    return self._nobody.__of__(self)
                else:
                    # anonymous can't authorize or we're not top-level user
                    # folder
                    return None
            else:
                # We found a user and the user wasn't the emergency user.
                # We need to authorize the user against the published object.
                if self.authorize(user, a, c, n, v, roles):
                    return user.__of__(self)
                # That didn't work.  Try to authorize the anonymous user.
                elif self._isTop() and self.authorize(
                    self._nobody, a, c, n, v, roles):
                    return self._nobody.__of__(self)
                else:
                    # we can't authorize the user, and we either can't
                    # authorize nobody against the published object or
                    # we're not top-level
                    return None

    def _getobcontext(self, v, request):
        """
        v is the object (value) we're validating access to
        n is the name used to access the object
        a is the object the object was accessed through
        c is the physical container of the object
        """
        if len(request.steps) == 0: # someone deleted root index_html
            request.RESPONSE.notFoundError('no default view (root index_html'
                                           ' was probably deleted)')
        n = request.steps[-1]
        # default to accessed and container as v.aq_parent
        a = c = request['PARENTS'][0]
        # try to find actual container
        inner = getattr(v, 'aq_inner', v)
        innerparent = getattr(inner, 'aq_parent', None)
        if innerparent is not None:
            # this is not a method, we needn't treat it specially
            c = innerparent
        elif hasattr(v, 'im_self'):
            # this is a method, we need to treat it specially
            c = v.im_self
            c = getattr(v, 'aq_inner', v)
        request_container = getattr(request['PARENTS'][-1], 'aq_parent', [])
        # if pub's aq_parent or container is the request container, it
        # means pub was accessed from the root
        if a is request_container:
            a = request['PARENTS'][-1]
        if c is request_container:
            c = request['PARENTS'][-1]
            
        return a, c, n, v

    def _isTop(self):
        try:
            return self.aq_parent.aq_base.isTopLevelPrincipiaApplicationObject
        except:
            return 0

    def __len__(self):
        return 1

    _mainUser=DTMLFile('dtml/mainUser', globals())
    _add_User=DTMLFile('dtml/addUser', globals(),
                       remote_user_mode__=_remote_user_mode)
    _editUser=DTMLFile('dtml/editUser', globals(),
                       remote_user_mode__=_remote_user_mode)
    manage=manage_main=_mainUser
    manage_main._setName('manage_main')

    _userFolderProperties = DTMLFile('dtml/userFolderProps', globals())

    def manage_userFolderProperties(self, REQUEST=None,
                                    manage_tabs_message=None):
        """
        """
        return self._userFolderProperties(
            self, REQUEST, manage_tabs_message=manage_tabs_message,
            management_view='Properties')

    def manage_setUserFolderProperties(self, encrypt_passwords=0,
                                       update_passwords=0,
                                       maxlistusers=DEFAULTMAXLISTUSERS,
                                       REQUEST=None):
        """
        Sets the properties of the user folder.
        """
        self.encrypt_passwords = not not encrypt_passwords
        try:
            self.maxlistusers = int(maxlistusers)
        except ValueError:
            self.maxlistusers = DEFAULTMAXLISTUSERS
        if encrypt_passwords and update_passwords:
            changed = 0
            for u in self.getUsers():
                pw = u._getPassword()
                if not self._isPasswordEncrypted(pw):
                    pw = self._encryptPassword(pw)
                    self.manage_editUser(u.getUserName(), pw, u.getRoles(),
                                         u.getDomains())
                    changed = changed + 1
            if REQUEST is not None:
                if not changed:
                    msg = 'All passwords already encrypted.'
                else:
                    msg = 'Encrypted %d password(s).' % changed
                return self.manage_userFolderProperties(
                    REQUEST, manage_tabs_message=msg)
            else:
                return changed
        else:
            if REQUEST is not None:
                return self.manage_userFolderProperties(
                    REQUEST, manage_tabs_message='Saved changes.')

    def _isPasswordEncrypted(self, pw):
        return AuthEncoding.is_encrypted(pw)

    def _encryptPassword(self, pw):
        return AuthEncoding.pw_encrypt(pw, 'SSHA')

    def domainSpecValidate(self, spec):
        for ob in spec:
            sz=len(ob)
            am = addr_match(ob)
            hm = host_match(ob)
            if am or hm:
                if am: am = am.end()
                else: am = -1
                if hm: hm = hm.end()
                else: hm = -1
                if not ( (am == sz) or (hm == sz) ):
                    return 0
        return 1

    def _addUser(self,name,password,confirm,roles,domains,REQUEST=None):
        if not name:
            return MessageDialog(
                   title  ='Illegal value', 
                   message='A username must be specified',
                   action ='manage_main')
        if not password or not confirm:
            if not domains:
                return MessageDialog(
                   title  ='Illegal value', 
                   message='Password and confirmation must be specified',
                   action ='manage_main')
        if self.getUser(name) or (self._emergency_user and
                                  name == self._emergency_user.getUserName()):
            return MessageDialog(
                   title  ='Illegal value', 
                   message='A user with the specified name already exists',
                   action ='manage_main')
        if (password or confirm) and (password != confirm):
            return MessageDialog(
                   title  ='Illegal value', 
                   message='Password and confirmation do not match',
                   action ='manage_main')
        
        if not roles: roles=[]
        if not domains: domains=[]

        if domains and not self.domainSpecValidate(domains):
            return MessageDialog(
                   title  ='Illegal value', 
                   message='Illegal domain specification',
                   action ='manage_main')
        if self.encrypt_passwords:
            password = self._encryptPassword(password)
        self.manage_addUser(name, password, roles, domains)
        if REQUEST: return self._mainUser(self, REQUEST)


    def _changeUser(self,name,password,confirm,roles,domains,REQUEST=None):
        if password == 'password' and confirm == 'pconfirm':
            # Protocol for editUser.dtml to indicate unchanged password
            password = confirm = None
        if not name:
            return MessageDialog(
                   title  ='Illegal value', 
                   message='A username must be specified',
                   action ='manage_main')
        if password == confirm == '':
            if not domains:
                return MessageDialog(
                   title  ='Illegal value', 
                   message='Password and confirmation must be specified',
                   action ='manage_main')
        if not self.getUser(name):
            return MessageDialog(
                   title  ='Illegal value', 
                   message='Unknown user',
                   action ='manage_main')
        if (password or confirm) and (password != confirm):
            return MessageDialog(
                   title  ='Illegal value', 
                   message='Password and confirmation do not match',
                   action ='manage_main')

        if not roles: roles=[]
        if not domains: domains=[]

        if domains and not self.domainSpecValidate(domains):
            return MessageDialog(
                   title  ='Illegal value', 
                   message='Illegal domain specification',
                   action ='manage_main')
        if password is not None and self.encrypt_passwords:
            password = self._encryptPassword(password)
        self.manage_editUser(name, password, roles, domains)
        if REQUEST: return self._mainUser(self, REQUEST)

    def _delUsers(self,names,REQUEST=None):
        if not names:
            return MessageDialog(
                   title  ='Illegal value', 
                   message='No users specified',
                   action ='manage_main')
        self.manage_delUsers(names)
        if REQUEST: return self._mainUser(self, REQUEST)

    def manage_users(self,submit=None,REQUEST=None,RESPONSE=None):
        """This method handles operations on users for the web based forms
           of the ZMI. Use of this method by application code is deprecated.
           Use the manage_addUser, manage_editUser and manage_delUsers APIs
           instead."""
        if submit=='Add...':
            return self._add_User(self, REQUEST)

        if submit=='Edit':
            try:    user=self.getUser(reqattr(REQUEST, 'name'))
            except: return MessageDialog(
                    title  ='Illegal value',
                    message='The specified user does not exist',
                    action ='manage_main')
            return self._editUser(self,REQUEST,user=user,password=user.__)

        if submit=='Add':
            name    =reqattr(REQUEST, 'name')
            password=reqattr(REQUEST, 'password')
            confirm =reqattr(REQUEST, 'confirm')
            roles   =reqattr(REQUEST, 'roles')
            domains =reqattr(REQUEST, 'domains')
            return self._addUser(name,password,confirm,roles,domains,REQUEST)

        if submit=='Change':
            name    =reqattr(REQUEST, 'name')
            password=reqattr(REQUEST, 'password')
            confirm =reqattr(REQUEST, 'confirm')
            roles   =reqattr(REQUEST, 'roles')
            domains =reqattr(REQUEST, 'domains')
            return self._changeUser(name,password,confirm,roles,
                                    domains,REQUEST)

        if submit=='Delete':
            names=reqattr(REQUEST, 'names')
            return self._delUsers(names,REQUEST)

        return self._mainUser(self, REQUEST)

    def user_names(self):
        return self.getUserNames()

    def manage_beforeDelete(self, item, container):
        if item is self:
            try: del container.__allow_groups__
            except: pass

    def manage_afterAdd(self, item, container):
        if item is self:
            if hasattr(self, 'aq_base'): self=self.aq_base
            container.__allow_groups__=self

    def __creatable_by_emergency_user__(self): return 1

    def _setId(self, id):
        if id != self.id:
            raise Globals.MessageDialog(
                title='Invalid Id',
                message='Cannot change the id of a UserFolder',
                action ='./manage_main',)


    # Domain authentication support. This is a good candidate to
    # become deprecated in future Zope versions.

    def setDomainAuthenticationMode(self, domain_auth_mode):
        """Set the domain-based authentication mode. By default, this
           mode is off due to the high overhead of the operation that
           is incurred for all anonymous accesses. If you have the
           'Manage Users' permission, you can call this method via
           the web, passing a boolean value for domain_auth_mode to
           turn this behavior on or off."""
        v = self._domain_auth_mode = domain_auth_mode and 1 or 0
        return 'Domain authentication mode set to %d' % v

    def domainAuthModeEnabled(self):
        """ returns true if domain auth mode is set to true"""
        return getattr(self, '_domain_auth_mode', None)

class UserFolder(BasicUserFolder):
    """Standard UserFolder object

    A UserFolder holds User objects which contain information
    about users including name, password domain, and roles.
    UserFolders function chiefly to control access by authenticating
    users and binding them to a collection of roles."""

    meta_type='User Folder'
    id       ='acl_users'
    title    ='User Folder'
    icon     ='p_/UserFolder'

    def __init__(self):
        self.data=PersistentMapping()

    def getUserNames(self):
        """Return a list of usernames"""
        names=self.data.keys()
        names.sort()
        return names

    def getUsers(self):
        """Return a list of user objects"""
        data=self.data
        names=data.keys()
        names.sort()
        users=[]
        f=users.append
        for n in names:
            f(data[n])
        return users

    def getUser(self, name):
        """Return the named user object or None"""
        return self.data.get(name, None)

    def manage_addUser(self, name, password, roles, domains):
        """API method used to create a new user object."""
        self.data[name]=User(name,password,roles,domains)

    def manage_editUser(self, name, password, roles, domains):
        """API method used to change the attributes of a user."""
        user=self.data[name]
        if password is not None:
            user.__=password
        user.roles=roles
        user.domains=domains

    def manage_delUsers(self, names):
        """API method used to delete one or more user objects."""
        for name in names:
            del self.data[name]

    def _createInitialUser(self):
        """
        If there are no users or only one user in this user folder,
        populates from the 'inituser' file in INSTANCE_HOME.
        We have to do this even when there is already a user
        just in case the initial user ignored the setup messages.
        We don't do it for more than one user to avoid
        abuse of this mechanism.
        Called only by OFS.Application.initialize().
        """
        if len(self.data) <= 1:
            info = readUserAccessFile('inituser')
            if info:
                name, password, domains, remote_user_mode = info
                self.manage_delUsers(self.getUserNames())
                self.manage_addUser(name, password, ('Manager',), domains)
                try:
                    os.remove(os.path.join(INSTANCE_HOME, 'inituser'))
                except:
                    pass


Globals.default__class_init__(UserFolder)






def manage_addUserFolder(self,dtself=None,REQUEST=None,**ignored):
    """ """
    f=UserFolder()
    self=self.this()
    try:    self._setObject('acl_users', f)
    except: return MessageDialog(
                   title  ='Item Exists',
                   message='This object already contains a User Folder',
                   action ='%s/manage_main' % REQUEST['URL1'])
    self.__allow_groups__=f
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')


def rolejoin(roles, other):
    dict={}
    for role in roles:
        dict[role]=1
    for role in other:
        dict[role]=1
    roles=dict.keys()
    roles.sort()
    return roles

addr_match=re.compile(r'[\d.]*').match
host_match=re.compile(r'[-\w.]*').match

def domainSpecMatch(spec, request):
    host=''
    addr=''

    
    # Fast exit for the match-all case
    if len(spec) == 1 and spec[0] == '*':
        return 1

    if request.has_key('REMOTE_HOST'):
        host=request['REMOTE_HOST']

    if request.has_key('REMOTE_ADDR'):
        addr=request['REMOTE_ADDR']

    if not host and not addr:
        return 0

    if not host:
        try:    host=socket.gethostbyaddr(addr)[0]
        except: pass
    if not addr:
        try:    addr=socket.gethostbyname(host)
        except: pass


    _host=split(host, '.')
    _addr=split(addr, '.')
    _hlen=len(_host)
    _alen=len(_addr)
    
    for ob in spec:
        sz=len(ob)
        _ob=split(ob, '.')
        _sz=len(_ob)

        mo = addr_match(ob)
        if mo is not None:
            if mo.end(0)==sz: 
                fail=0
                for i in range(_sz):
                    a=_addr[i]
                    o=_ob[i]
                    if (o != a) and (o != '*'):
                        fail=1
                        break
                if fail:
                    continue
                return 1

        mo = host_match(ob)
        if mo is not None:
            if mo.end(0)==sz:
                if _hlen < _sz:
                    continue
                elif _hlen > _sz:
                    _item=_host[-_sz:]
                else:
                    _item=_host
                fail=0
                for i in range(_sz):
                    h=_item[i]
                    o=_ob[i]
                    if (o != h) and (o != '*'):
                        fail=1
                        break
                if fail:
                    continue
                return 1
    return 0


def absattr(attr):
    if callable(attr): return attr()
    return attr

def reqattr(request, attr):
    try:    return request[attr]
    except: return None

Super = UnrestrictedUser  # Note: use of the Super alias is deprecated.
