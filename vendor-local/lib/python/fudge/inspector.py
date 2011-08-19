
"""Value inspectors that can be passed to :func:`fudge.Fake.with_args` for more 
expressive argument matching.  

As a mnemonic device, 
an instance of the :class:`fudge.inspector.ValueInspector` is available as "arg" :

.. doctest::
    
    >>> import fudge
    >>> from fudge.inspector import arg
    >>> image = fudge.Fake("image").expects("save").with_args(arg.endswith(".jpg"))

In other words, this declares that the first argument to ``image.save()`` 
should end with the suffix ".jpg"
    
.. doctest::
    :hide:
    
    >>> fudge.clear_expectations()

"""
import warnings

from fudge.util import fmt_val, fmt_dict_vals

__all__ = ['arg']

class ValueInspector(object):
    """Dispatches tests to inspect values. 
    """
    
    def any(self):
        """Match any value.
        
        This is pretty much just a placeholder for when you 
        want to inspect multiple arguments but don't care about 
        all of them.
        
        .. doctest::
            
            >>> import fudge
            >>> from fudge.inspector import arg
            >>> db = fudge.Fake("db")
            >>> db = db.expects("transaction").with_args(
            ...             "insert", isolation_level=arg.any())
            ... 
            >>> db.transaction("insert", isolation_level="lock")
            >>> fudge.verify()
        
        This also passes:
        
        .. doctest::
            :hide:
            
            >>> fudge.clear_calls()
            
        .. doctest::
        
            >>> db.transaction("insert", isolation_level="autocommit")
            >>> fudge.verify()
        
        .. doctest::
            :hide:
            
            >>> fudge.clear_expectations()
        
        """
        return AnyValue()

    def any_value(self):
        """**DEPRECATED**: use :func:`arg.any() <fudge.inspector.ValueInspector.any>`
        """
        warnings.warn('arg.any_value() is deprecated in favor of arg.any()')
        return self.any()

    def contains(self, part):
        """Ensure that a value contains some part.
        
        This is useful for when you only care that a substring or subelement 
        exists in a value.
        
        .. doctest::
            
            >>> import fudge
            >>> from fudge.inspector import arg
            >>> addressbook = fudge.Fake().expects("import_").with_args(
            ...                                     arg.contains("Baba Brooks"))
            ... 
            >>> addressbook.import_("Bill Brooks; Baba Brooks; Henry Brooks;")
            >>> fudge.verify()
        
        .. doctest::
            :hide:
            
            >>> fudge.clear_expectations()
        
        Since contains() just invokes the __in__() method, checking that a list 
        item is present works as expected :
        
        .. doctest::
            
            >>> colorpicker = fudge.Fake("colorpicker")
            >>> colorpicker = colorpicker.expects("select").with_args(arg.contains("red"))
            >>> colorpicker.select(["green","red","blue"])
            >>> fudge.verify()
        
        .. doctest::
            :hide:
            
            >>> fudge.clear_expectations()
            
        """
        return Contains(part)
    
    def endswith(self, part):
        """Ensure that a value ends with some part.
        
        This is useful for when values with dynamic parts that are hard to replicate.
        
        .. doctest::
            
            >>> import fudge
            >>> from fudge.inspector import arg
            >>> tmpfile = fudge.Fake("tempfile").expects("mkname").with_args(
            ...                                             arg.endswith(".tmp"))
            ... 
            >>> tmpfile.mkname("7AakkkLazUUKHKJgh908JKjlkh.tmp")
            >>> fudge.verify()
            
        .. doctest::
            :hide:
            
            >>> fudge.clear_expectations()
            
        """
        return Endswith(part)
    
    def has_attr(self, **attributes):
        """Ensure that an object value has at least these attributes.
        
        This is useful for testing that an object has specific attributes.
        
        .. doctest::
            
            >>> import fudge
            >>> from fudge.inspector import arg
            >>> db = fudge.Fake("db").expects("update").with_args(arg.has_attr(
            ...                                                       first_name="Bob",
            ...                                                       last_name="James" ))
            ... 
            >>> class User:
            ...     first_name = "Bob"
            ...     last_name = "James"
            ...     job = "jazz musician" # this is ignored
            ... 
            >>> db.update(User())
            >>> fudge.verify()
        
        In case of error, the other object's __repr__ will be invoked:
        
        .. doctest::
            :hide:
            
            >>> fudge.clear_calls()
        
        .. doctest::
            
            >>> class User:
            ...     first_name = "Bob"
            ... 
            ...     def __repr__(self):
            ...         return repr(dict(first_name=self.first_name))
            ... 
            >>> db.update(User())
            Traceback (most recent call last):
            ...
            AssertionError: fake:db.update(arg.has_attr(first_name='Bob', last_name='James')) was called unexpectedly with args ({'first_name': 'Bob'})
            
            
        .. doctest::
            :hide:
            
            >>> fudge.clear_expectations()
            
        """
        return HasAttr(**attributes)
    
    def passes_test(self, test):
        """Check that a value passes some test.
        
        For custom assertions you may need to create your own callable 
        to inspect and verify a value.
        
        .. doctest::
            
            >>> def is_valid(s):
            ...     if s in ('active','deleted'):
            ...         return True
            ...     else:
            ...         return False
            ... 
            >>> import fudge
            >>> from fudge.inspector import arg
            >>> system = fudge.Fake("system")
            >>> system = system.expects("set_status").with_args(arg.passes_test(is_valid))
            >>> system.set_status("active")
            >>> fudge.verify()
            
        .. doctest::
            :hide:
            
            >>> fudge.clear_calls()
        
        The callable you pass takes one argument, the value, and should return 
        True if it's an acceptable value or False if not.
        
        .. doctest::
            
            >>> system.set_status("sleep") # doctest: +ELLIPSIS
            Traceback (most recent call last):
            ...
            AssertionError: fake:system.set_status(arg.passes_test(<function is_valid at...)) was called unexpectedly with args ('sleep')
        
        .. doctest::
            :hide:
            
            >>> fudge.clear_expectations()
        
        If it makes more sense to perform assertions in your test function then 
        be sure to return True :
        
            >>> def is_valid(s):
            ...     assert s in ('active','deleted'), (
            ...         "Unexpected status value: %s" % s)
            ...     return True
            ... 
            >>> import fudge
            >>> from fudge.inspector import arg
            >>> system = fudge.Fake("system")
            >>> system = system.expects("set_status").with_args(arg.passes_test(is_valid))
            >>> system.set_status("sleep")
            Traceback (most recent call last):
            ...
            AssertionError: Unexpected status value: sleep
        
        .. doctest::
            :hide:
            
            >>> fudge.clear_expectations()
            
        """
        return PassesTest(test)
    
    def startswith(self, part):
        """Ensure that a value starts with some part.
        
        This is useful for when values with dynamic parts that are hard to replicate.
        
        .. doctest::
            
            >>> import fudge
            >>> from fudge.inspector import arg
            >>> keychain = fudge.Fake("keychain").expects("accept_key").with_args(
            ...                                                     arg.startswith("_key"))
            ... 
            >>> keychain.accept_key("_key-18657yojgaodfty98618652olkj[oollk]")
            >>> fudge.verify()
            
        .. doctest::
            :hide:
            
            >>> fudge.clear_expectations()
            
        """
        return Startswith(part)

arg = ValueInspector()

class ValueTest(object):
    
    arg_method = None
    __test__ = False # nose
    
    def __eq__(self, other):
        raise NotImplementedError()
    
    def _repr_argspec(self):
        raise NotImplementedError()
    
    def __str__(self):
        return self._repr_argspec()
    
    def __unicode__(self):
        return self._repr_argspec()
    
    def __repr__(self):
        return self._repr_argspec()
    
    def _make_argspec(self, arg):
        if self.arg_method is None:
            raise NotImplementedError(
                "%r must have set attribute arg_method" % self.__class__)
        return "arg." + self.arg_method + "(" + arg + ")"

class Stringlike(ValueTest):
    
    def __init__(self, part):
        self.part = part
        
    def _repr_argspec(self):
        return self._make_argspec(fmt_val(self.part))
    
    def stringlike(self, value):
        if isinstance(value, (str, unicode)):
            return value
        else:
            return str(value)
    
    def __eq__(self, other):
        check_stringlike = getattr(self.stringlike(other), self.arg_method)
        return check_stringlike(self.part)

class Startswith(Stringlike):
    arg_method = "startswith"
    
class Endswith(Stringlike):
    arg_method = "endswith"

class HasAttr(ValueTest):
    arg_method = "has_attr"
    
    def __init__(self, **attributes):
        self.attributes = attributes
        
    def _repr_argspec(self):
        return self._make_argspec(", ".join(sorted(fmt_dict_vals(self.attributes))))
    
    def __eq__(self, other):
        for name, value in self.attributes.items():
            if not hasattr(other, name):
                return False
            if getattr(other, name) != value:
                return False
        
        return True

class AnyValue(ValueTest):
    arg_method = "any"
    
    def __eq__(self, other):
        # will match anything:
        return True
        
    def _repr_argspec(self):
        return self._make_argspec("")

class Contains(ValueTest):
    arg_method = "contains"
    
    def __init__(self, part):
        self.part = part
    
    def _repr_argspec(self):
        return self._make_argspec(fmt_val(self.part))
    
    def __eq__(self, other):
        if self.part in other:
            return True
        else:
            return False
        
class PassesTest(ValueTest):
    arg_method = "passes_test"
    
    def __init__(self, test):
        self.test = test
    
    def __eq__(self, other):
        return self.test(other)
    
    def _repr_argspec(self):
        return self._make_argspec(repr(self.test))

