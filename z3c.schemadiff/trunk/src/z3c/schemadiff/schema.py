from zope import interface

from interfaces import IFieldDiff

def diff(source, target, *interfaces):
    if not len(interfaces):
        interfaces = interface.providedBy(source)
        
    results = {}

    for iface in interfaces:
        for name in iface.names():
            field = iface[name]
            bound = field.bind(source)

            try:
                diff = IFieldDiff(bound)
            except TypeError:
                continue

            source_value = bound.query(source, field.default)
            target_value = bound.query(target, field.default)

            if source_value is None or target_value is None:
                continue

            if diff.lines is not None:
                result = diff.lines(source_value), diff.lines(target_value)
            else:
                result = diff.html_diff(source_value, target_value)
                
            results[field] = result

    return results
    
