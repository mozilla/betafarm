
try:
    from functools import wraps
except ImportError:
    # for python < 2.5... this is a limited set of what we need to do
    # with a wrapped function :
    def wraps(f):
        def wrap_with_f(new_f):
            new_f.__name__ = f.__name__
            if hasattr(f, '__module__'):
                new_f.__module__ = f.__module__
            return new_f
        return wrap_with_f

def fmt_val(val, shorten=True):
    """Format a value for inclusion in an 
    informative text string.
    """
    val = repr(val)
    max = 50
    if shorten:
        if len(val) > max:
            close = val[-1]
            val = val[0:max-4] + "..."
            if close in (">", "'", '"', ']', '}', ')'):
                val = val + close
    return val

def fmt_dict_vals(dict_vals, shorten=True):
    """Returns list of key=val pairs formatted
    for inclusion in an informative text string.
    """
    items = dict_vals.items()
    if not items:
        return [fmt_val(None, shorten=shorten)]
    return ["%s=%s" % (k, fmt_val(v, shorten=shorten)) for k,v in items]
