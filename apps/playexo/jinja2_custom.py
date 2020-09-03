import jinja2
from django.utils.safestring import SafeString



def firstof(*args):
    return next(iter([i for i in args if i]), "")



def capfirst(s):
    return s[0].upper() + s[1:]



def make_list(s):
    return list(str(s))



def first(elem):
    return elem[0] if elem else None



def component(elem):
    selector = elem["selector"]
    cid = elem["cid"]
    return SafeString("<%s cid='%s'></%s>" % (selector, cid, selector))



def environment(**options):
    env = jinja2.Environment(**options)
    env.globals.update({
        'firstof':   firstof,
        'capfirst':  capfirst,
        'make_list': make_list,
        'first':     first,
        "int":       int,
        "component": component
    })
    env.filters["component"] = component
    return env



class CustomUndefined(jinja2.Undefined):
    
    def _fail_with_undefined_error(self, *args, **kwargs):
        return ''
    
    
    __add__ = __radd__ = __mul__ = __rmul__ = __div__ = __rdiv__ = \
        __truediv__ = __rtruediv__ = __floordiv__ = __rfloordiv__ = \
        __mod__ = __rmod__ = __pos__ = __neg__ = __call__ = \
        __getitem__ = __lt__ = __le__ = __gt__ = __ge__ = __int__ = \
        __float__ = __complex__ = __pow__ = __rpow__ = \
        _fail_with_undefined_error
