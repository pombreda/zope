"""BeforeTraverse interface and helper classes"""

# Interface

def registerBeforeTraverse(container, object, app_handle, priority=99):
    """Register an object to be called before a container is traversed.

    'app_handle' should be a string or other hashable value that
    distinguishes the application of this object, and which must
    be used in order to unregister the object.

    If the container will be pickled, the object must be a callable class
    instance, not a function or method.

    'priority' is optional, and determines the relative order in which
    registered objects will be called.
    """
    btr = getattr(container, '__before_traverse__', {})
    btr[(priority, app_handle)] = object
    rewriteBeforeTraverse(container, btr)

def unregisterBeforeTraverse(container, app_handle):
    """Unregister a __before_traverse__ hook object, given its 'app_handle'.

    Returns a list of unregistered objects."""
    btr = getattr(container, '__before_traverse__', {})
    objects = []
    for k in btr.keys():
        if k[1] == app_handle:
            objects.append(btr[k])
            del btr[k]
    if objects:
        rewriteBeforeTraverse(container, btr)
    return objects

def queryBeforeTraverse(container, app_handle):
    """Find __before_traverse__ hook objects, given an 'app_handle'.

    Returns a list of (priority, object) pairs."""
    btr = getattr(container, '__before_traverse__', {})
    objects = []
    for k in btr.keys():
        if k[1] == app_handle:
            objects.append((k[0], btr[k]))
    return objects

# Implementation tools

def rewriteBeforeTraverse(container, btr):
    """Rewrite the list of __before_traverse__ hook objects"""
    container.__before_traverse__ = btr
    hookname = '__before_publishing_traverse__'
    dic = hasattr(container.__class__, hookname)
    bpth = container.__dict__.get(hookname, None)
    if isinstance(bpth, MultiHook):
        bpth = bpth._prior
    bpth = MultiHook(hookname, bpth, dic)
    setattr(container, hookname, bpth)
    
    keys = btr.keys()
    keys.sort()
    for key in keys:
        bpth.add(btr[key])

class MultiHook:
    """Class used to multiplex hook.

    MultiHook calls the named hook from the class of the container, then
    the prior hook, then all the hooks in its list.
    """
    def __init__(self, hookname, prior, defined_in_class):
        self._hookname = hookname
        self._prior = prior
        self._defined_in_class = defined_in_class
        self._list = []

    def __call__(self, container, request):
        if self._defined_in_class:
            # Assume it's an unbound method
            getattr(container.__class__, self._hookname)(container, request)
        prior = self._prior
        if prior is not None:
            prior(container, request)
        for cob in self._list:
            cob(container, request)

    def add(self, cob):
        self._list.append(cob)

# Helper class

class NameCaller:
    """Class used to proxy sibling objects by name.

    When called with a container and request object, it gets the named
    attribute from the container and calls it.  If the name is not
    found, it fails silently.

    >>> registerBeforeTraverse(folder, NameCaller('preop'), 'XApp')
    """

    def __init__(self, name):
        self.name = name

    def __call__(self, container, request):
        try:
            meth = getattr(container, self.name)
        except AttributeError:
            return

        args = getattr(getattr(meth, 'func_code', None), 'co_argcount', 2)
        apply(meth, (container, request, None)[:args])
    
