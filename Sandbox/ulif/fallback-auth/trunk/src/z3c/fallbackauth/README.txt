================================
Principal Registry Authenticator
================================

Principal registry authenticators provide an authenticator 'frontend'
to the global principal registry. Such, you can use it to authenticate
against principals in the global registry.

Because the global principal registry is limited in functionality
(compared to other principal containers), you cannot modify nor remove
principals defined therein, except you ask the principal registry
directly.

The principal registry authenticator offers a plain fallback solution,
you can put at the end of the list of authenticators in your
PAU. Such, when every other authenticator fails to authenticate a
user, the users defined in ``site.zcml`` should still be able to
login.

Different to other autenticators, we create principal registry
authenticators *without* a prefix:

  >>> from z3c.fallbackauth.authplugins import PrincipalRegistryAuthenticator
  >>> principals = PrincipalRegistryAuthenticator()


Principal registry authenticators do not support adding of items. We
can, however add principals to the global principal registry:

  >>> from zope.app.security.principalregistry import principalRegistry
  >>> reg = principalRegistry
  >>> p1 = reg.definePrincipal('p1', 'Tim Peters', 'Sir Tim Peters',
  ...                          'tim', '123')
  >>> p1
  <zope.app.security.principalregistry.Principal object at 0x...>

  >>> p2 = reg.definePrincipal('p2', 'Jim Fulton', 'Sir Jim Fulton',
  ...                          'jim', '456') 


Authentication
--------------

Principal registry authenticators provide the `IAuthenticatorPlugin`
interface. When we provide suitable credentials:

  >>> from zope.testing.doctestunit import pprint
  >>> principals.authenticateCredentials({'login': 'tim', 
  ...                                     'password': '123'})
  PrincipalInfo(u'p1')

We get back a principal id and supplementary information, including
the principal title and description.  Note that the principal id is
*not* a concatenation of the principal-folder prefix and the name of
the principal-information object within the folder (as it is with
other authenticators), simply, because principal registry
authenticators have no prefix.

None is returned if the credentials are invalid:

  >>> principals.authenticateCredentials({'login': 'login1',
  ...                                     'password': '1234'})
  >>> principals.authenticateCredentials(42)

Search
------
Principal registry authenticators also provide the IQuerySchemaSearch
interface.  This supports both finding principal information based on
their ids:

  >>> principals.principalInfo('p1')
  PrincipalInfo(u'p1')

and searching for principals based on a search string:

  >>> list(principals.search({'search': 'ulto'}))
  [u'p2']

  >>> list(principals.search({'search': 'ULTO'}))
  [u'p2']

  >>> sorted(list(principals.search({'search': ''})))
  [u'p1', u'p2']

  >>> list(principals.search({'search': 'eek'}))
  []

  >>> list(principals.search({}))
  []

If there are a large number of matches:

  >>> for i in range(20):
  ...     i = str(i)
  ...     trash = reg.definePrincipal(''+i, 'Dude '+i, 'Dude '+i,
  ...                                 'jim' + i, i) 
  ...     #p = InternalPrincipal('l'+i, i, "Dude "+i)
  ...     #principals[i] = p

  >>> pprint(list(principals.search({'search': 'D'})))
  [u'0',
   u'1',
   u'10',
   u'11',
   u'12',
   u'13',
   u'14',
   u'15',
   u'16',
   u'17',
   u'18',
   u'19',
   u'2',
   u'3',
   u'4',
   u'5',
   u'6',
   u'7',
   u'8',
   u'9']

We can use batching parameters to specify a subset of results:

  >>> pprint(list(principals.search({'search': 'D'}, start=17)))
  [u'7',
   u'8',
   u'9']

  >>> pprint(list(principals.search({'search': 'D'}, batch_size=5)))
  [u'0',
   u'1',
   u'10',
   u'11',
   u'12']

  >>> pprint(list(principals.search({'search': 'D'}, start=5, batch_size=5)))
  [u'13',
   u'14',
   u'15',
   u'16',
   u'17']

Changing credentials not supported
----------------------------------
Credentials of a principal registry authenticator can *not* be
changed, because the principalRegistry, which is our 'principal
container', does not support changing of principals. 

So the usual techniques of modifying principal-information objects do
not change credentials:

  >>> p1.login = 'bob'
  >>> p1.password = 'eek'

  >>> p = principals.authenticateCredentials({'login': 'bob', 
  ...                                         'password': 'eek'})
  >>> p is None
  True

Removing principals not supported
---------------------------------
Due to the structure of principal registry, principals cannot be
removed:

  >>> del principals['p1']
  Traceback (most recent call last):
  ...
  TypeError:...object does not support item deletion

