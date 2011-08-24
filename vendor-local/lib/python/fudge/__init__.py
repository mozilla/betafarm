
"""Fudge is a module for replacing real objects with fakes (mocks, stubs, etc) while testing.

See :ref:`using-fudge` for common scenarios.

"""

__version__ = '1.0.3'
import os
import re
import sys
import thread
import warnings
from fudge.exc import FakeDeclarationError
from fudge.patcher import *
from fudge.util import wraps, fmt_val, fmt_dict_vals

__all__ = ['Fake', 'patch', 'test', 'clear_calls', 'verify',
           'clear_expectations']

class Registry(object):
    """An internal, thread-safe registry of expected calls.
    
    You do not need to use this directly, use Fake.expects(...), etc
    """
    
    def __init__(self):
        self.expected_calls = {}
        self.expected_call_order = {}
        self.call_stacks = []
    
    def __contains__(self, obj):
        return obj in self.get_expected_calls()
        
    def clear_actual_calls(self):
        for exp in self.get_expected_calls():
            exp.was_called = False
    
    def clear_all(self):
        self.clear_actual_calls()
        self.clear_expectations()
    
    def clear_calls(self):
        """Clears out any calls that were made on previously 
        registered fake objects and resets all call stacks.
        
        You do not need to use this directly.  Use fudge.clear_calls()
        """
        self.clear_actual_calls()
        for stack in self.call_stacks:
            stack.reset()
        for fake, call_order in self.get_expected_call_order().items():
            call_order.reset_calls()
    
    def clear_expectations(self):
        c = self.get_expected_calls()
        c[:] = []
        d = self.get_expected_call_order()
        d.clear()
        
    def expect_call(self, expected_call):
        c = self.get_expected_calls()
        c.append(expected_call)
        call_order = self.get_expected_call_order()
        if expected_call.fake in call_order:
            this_call_order = call_order[expected_call.fake]
            this_call_order.add_expected_call(expected_call)
    
    def get_expected_calls(self):
        self.expected_calls.setdefault(thread.get_ident(), [])
        return self.expected_calls[thread.get_ident()]
    
    def get_expected_call_order(self):
        self.expected_call_order.setdefault(thread.get_ident(), {})
        return self.expected_call_order[thread.get_ident()]
    
    def remember_expected_call_order(self, expected_call_order):
        ordered_fakes = self.get_expected_call_order()
        fake = expected_call_order.fake
        ## does nothing if called twice like:
        # Fake().remember_order().remember_order()
        ordered_fakes.setdefault(fake, expected_call_order)
    
    def register_call_stack(self, call_stack):
        self.call_stacks.append(call_stack)
    
    def verify(self):
        """Ensure all expected calls were called, 
        raise AssertionError otherwise.
        
        You do not need to use this directly.  Use fudge.verify()
        """
        try:
            for exp in self.get_expected_calls():
                exp.assert_called()
                exp.assert_times_called()
            for fake, call_order in self.get_expected_call_order().items():
                call_order.assert_order_met(finalize=True)
        finally:
            self.clear_calls()
        
registry = Registry()


def clear_calls():
    """Begin a new set of calls on fake objects.
    
    Specifically, clear out any calls that 
    were made on previously registered fake 
    objects and reset all call stacks.  
    You should call this any time you begin 
    making calls on fake objects.
    
    This is also available in :func:`fudge.patch`, :func:`fudge.test` and :func:`fudge.with_fakes`
    """
    registry.clear_calls()


def verify():
    """Verify that all methods have been called as expected.
    
    Specifically, analyze all registered fake 
    objects and raise an AssertionError if an 
    expected call was never made to one or more 
    objects.
    
    This is also available in :func:`fudge.patch`, :func:`fudge.test` and :func:`fudge.with_fakes`
    """
    registry.verify()


## Deprecated:

def start():
    """Start testing with fake objects.
    
    Deprecated.  Use :func:`fudge.clear_calls` instead.
    """
    warnings.warn(
        "fudge.start() has been deprecated.  Use fudge.clear_calls() instead", 
        DeprecationWarning, 3)
    clear_calls()


def stop():
    """Stop testing with fake objects.
    
    Deprecated.  Use :func:`fudge.verify` instead.
    """
    warnings.warn(
        "fudge.stop() has been deprecated.  Use fudge.verify() instead", 
        DeprecationWarning, 3)
    verify()

##


def clear_expectations():
    registry.clear_expectations()


def with_fakes(method):
    """Decorator that calls :func:`fudge.clear_calls` before method() and :func:`fudge.verify` afterwards.
    """
    @wraps(method)
    def apply_clear_and_verify(*args, **kw):
        clear_calls()
        method(*args, **kw)
        verify() # if no exceptions
    return apply_clear_and_verify


def test(method):
    """Decorator for a test that uses fakes directly (not patched).

    Most of the time you probably want to use :func:`fudge.patch` instead.
    
    .. doctest::
        :hide:
        
        >>> import fudge

    .. doctest::
        
        >>> @fudge.test
        ... def test():
        ...     db = fudge.Fake('db').expects('connect')
        ...     # do stuff...
        ... 
        >>> test()
        Traceback (most recent call last):
        ...
        AssertionError: fake:db.connect() was not called
    
    .. doctest::
        :hide:
        
        >>> fudge.clear_expectations()

    """
    @wraps(method)
    def clear_and_verify(*args, **kw):
        clear_expectations()
        clear_calls()
        try:
            v = method(*args, **kw)
            verify() # if no exceptions
        finally:
            clear_expectations()
        return v
    return clear_and_verify
test.__test__ = False # Nose: do not collect

class Call(object):
    """A call that can be made on a Fake object.
    
    You do not need to use this directly, use Fake.provides(...), etc
    
    index=None
        When numerical, this indicates the position of the call 
        (as in, a CallStack)
    
    callable=False
        Means this object acts like a function, not a method of an 
        object.
    
    call_order=ExpectedCallOrder()
        A call order to append each call to.  Default is None
    """
    
    def __init__(self, fake, call_name=None, index=None,
                 callable=False, call_order=None):
        self.fake = fake
        self.call_name = call_name
        self.call_replacement = None
        self.expected_arg_count = None
        self.expected_kwarg_count = None
        self.expected_args = None
        self.expected_kwargs = None
        self.expected_matching_args = None
        self.expected_matching_kwargs = None
        self.index = index
        self.exception_to_raise = None
        self.return_val = None
        self.was_called = False
        self.expected_times_called = None
        self.actual_times_called = 0
        self.callable = callable
        self.call_order = call_order
        
    def __call__(self, *args, **kwargs):
        self.was_called = True
        self.actual_times_called += 1
        if self.call_order:
            self.call_order.add_actual_call(self)
            self.call_order.assert_order_met(finalize=False)
        
        # make sure call count doesn't go over :
        if self.expected_times_called is not None and \
                self.actual_times_called > self.expected_times_called:
            raise AssertionError(
                '%s was called %s time(s). Expected %s.' % (
                    self, self.actual_times_called,
                    self.expected_times_called))
        
        return_val = None
        replacement_return = None
        
        if self.call_replacement:
            replacement_return = self.call_replacement(*args, **kwargs)
        if self.return_val is not None:
            # this wins:
            return_value = self.return_val
        else:
            # but it is intuitive to otherwise 
            # return the replacement's return:
            return_value = replacement_return
        
        # determine whether we should inspect arguments or not:
        with_args = (self.expected_args or self.expected_kwargs)
        
        if with_args: 
            # check keyword args first because of python arg coercion...
            if self.expected_kwargs is None:
                self.expected_kwargs = {} # empty **kw
            if self.expected_kwargs != kwargs:
                raise AssertionError(
                    "%s was called unexpectedly with args %s" % (
                            self, 
                            self._repr_call(args, kwargs,
                                            shorten_long_vals=False)))
            
            if self.expected_args is None:
                self.expected_args = tuple([]) # empty *args
            if self.expected_args != args:
                raise AssertionError(
                    "%s was called unexpectedly with args %s" % (
                            self, 
                            self._repr_call(args, kwargs,
                                            shorten_long_vals=False)))
        
        # now check for matching keyword args.
        # i.e. keyword args that are only checked if the call provided them
        if self.expected_matching_kwargs:
            for expected_arg, expected_value in \
                                self.expected_matching_kwargs.items():
                if expected_arg in kwargs:
                    if expected_value != kwargs[expected_arg]:
                        raise AssertionError(
                            "%s was called unexpectedly with args %s" % (
                                    self, 
                                    self._repr_call(args, 
                                        {expected_arg: kwargs[expected_arg]}, 
                                        shorten_long_vals=False))
                        )
        
        # now check for matching args.
        # i.e. args that are only checked if the call provided them
        if self.expected_matching_args:
            if self.expected_matching_args != args:
                raise AssertionError(
                    "%s was called unexpectedly with args %s" % (
                            self, 
                            self._repr_call(args, kwargs,
                                            shorten_long_vals=False)))
                            
        # determine whether we should inspect argument counts or not:
        with_arg_counts = (self.expected_arg_count is not None or 
                           self.expected_kwarg_count is not None)
        
        if with_arg_counts: 
            if self.expected_arg_count is None:
                self.expected_arg_count = 0
            if len(args) != self.expected_arg_count:
                raise AssertionError(
                    "%s was called with %s arg(s) but expected %s" % (
                        self, len(args), self.expected_arg_count))
            
            if self.expected_kwarg_count is None:
                self.expected_kwarg_count = 0
            if len(kwargs.keys()) != self.expected_kwarg_count:
                raise AssertionError(
                    "%s was called with %s keyword arg(s) but expected %s" % (
                        self, len(kwargs.keys()), self.expected_kwarg_count))
        
        if self.exception_to_raise is not None:
            raise self.exception_to_raise
        
        return return_value
    
    ## hmmm, arg diffing (for Call().__call__()) needs more thought
        
    # def _arg_diff(self, actual_args, expected_args):
    #     """return differnce between keywords"""
    #     if len(actual_args) > len(expected_args):
    #         pass
    #             
    # 
    # def _keyword_diff(self, actual_kwargs, expected_kwargs):
    #     """returns difference between keywords.
    #     """
    #     expected_keys = set(expected_kwargs.keys())
    #     if (len(expected_keys)<=1 and len(actual_kwargs.keys())<=1):
    #         # no need for detailed messages
    #         if actual_kwargs == expected_kwargs:
    #             return (True, "")
    #         else:
    #             return (False, "")
    #         
    #     for k,v in actual_kwargs.items():
    #         if k not in expected_keys:
    #             return (False, "keyword %r was not expected" % k)
    #         if v != expected_kwargs[k]:
    #             return (False, "%s=%r != %s=%r" % (k, v, k, expected_kwargs[k]))
    #         expected_keys.remove(k)
    #     
    #     exp_key_len = len(expected_keys)
    #     if exp_key_len:
    #         these = exp_key_len==1 and "this keyword" or "these keywords"
    #         return (False, "%s never showed up: %r" % (these, tuple(expected_keys)))
    #     
    #     return (True, "")

    def _repr_call(self, expected_args, expected_kwargs, shorten_long_vals=True):
        args = []
        if expected_args:
            args.extend([fmt_val(a, shorten=shorten_long_vals) for a in expected_args])
        if expected_kwargs:
            args.extend(fmt_dict_vals(expected_kwargs, shorten=shorten_long_vals))
        if args:
            call = "(%s)" % ", ".join(args)
        else:
            call = "()"
        return call
    
    def __repr__(self):
        cls_name = repr(self.fake)
        if self.call_name and not self.callable:
            call = "%s.%s" % (cls_name, self.call_name)
        else:
            call = "%s" % cls_name
        call = "%s%s" % (call, self._repr_call(self.expected_args, self.expected_kwargs))
        if self.index is not None:
            call = "%s[%s]" % (call, self.index)
        return call
    
    def get_call_object(self):
        """return self.
        
        this exists for compatibility with :class:`CallStack`
        """
        return self

    def assert_times_called(self):
        if self.expected_times_called is not None and \
                self.actual_times_called != self.expected_times_called:
            raise AssertionError(
                '%s was called %s time(s). Expected %s.' % (
                    self, self.actual_times_called, self.expected_times_called))
            
    

class ExpectedCall(Call):
    """An expectation that a call will be made on a Fake object.
    
    You do not need to use this directly, use Fake.expects(...), etc
    """
    
    def __init__(self, *args, **kw):
        super(ExpectedCall, self).__init__(*args, **kw)
        registry.expect_call(self)
    
    def assert_called(self):
        if not self.was_called:
            raise AssertionError("%s was not called" % (self))

class ExpectedCallOrder(object):
    """An expectation that calls should be called in a specific order."""
    
    def __init__(self, fake):
        self.fake = fake
        self._call_order = []
        self._actual_calls = []
    
    def __repr__(self):
        return "%r(%r)" % (self.fake, self._call_order)
    
    __str__ = __repr__
    
    def _repr_call_list(self, call_list):
        if not len(call_list):
            return "no calls"
        else:
            stack = ["#%s %r" % (i+1,c) for i,c in enumerate(call_list)]
            stack.append("end")
            return ", ".join(stack)
    
    def add_expected_call(self, call):
        self._call_order.append(call)
    
    def add_actual_call(self, call):
        self._actual_calls.append(call)
    
    def assert_order_met(self, finalize=False):
        """assert that calls have been made in the right order."""
        error = None
        actual_call_len = len(self._actual_calls)
        expected_call_len = len(self._call_order)
        
        if actual_call_len == 0:
            error = "Not enough calls were made"
        else:
            for i,call in enumerate(self._call_order):
                if actual_call_len < i+1:
                    if not finalize:
                        # we're not done asserting calls so 
                        # forget about not having enough calls
                        continue
                        
                    calls_made = len(self._actual_calls)
                    if calls_made == 1:
                        error = "Only 1 call was made"
                    else:
                        error = "Only %s calls were made" % calls_made
                    break
                    
                ac_call = self._actual_calls[i]
                if ac_call is not call:
                    error = "Call #%s was %r" % (i+1, ac_call)
                    break
            
            if not error:
                if actual_call_len > expected_call_len:
                    # only show the first extra call since this 
                    # will be triggered before all calls are finished:
                    error = "#%s %s was unexpected" % (
                        expected_call_len+1,
                        self._actual_calls[expected_call_len]
                    )
                
        if error:
            msg = "%s; Expected: %s" % (
                    error, self._repr_call_list(self._call_order))
            raise AssertionError(msg)
    
    def reset_calls(self):
        self._actual_calls[:] = []

class CallStack(object):
    """A stack of :class:`Call` objects
    
    Calling this object behaves just like Call except 
    the Call instance you operate on gets changed each time __call__() is made
    
    expected=False
        When True, this indicates that the call stack was derived 
        from an expected call.  This is used by Fake to register 
        each call on the stack.
    
    call_name
        Name of the call
        
    """
    
    def __init__(self, fake, initial_calls=None, expected=False, call_name=None):
        self.fake = fake
        self._pointer = 0 # position of next call to be made (can be reset)
        self._calls = []
        if initial_calls is not None:
            for c in initial_calls:
                self.add_call(c)
        self.expected = expected
        self.call_name = call_name
        registry.register_call_stack(self)
    
    def __iter__(self):
        for c in self._calls:
            yield c
    
    def __repr__(self):
        return "<%s for %r>" % (self.__class__.__name__, self._calls)
    
    __str__ = __repr__
            
    def add_call(self, call):
        self._calls.append(call)
        call.index = len(self._calls)-1
    
    def get_call_object(self):
        """returns the last *added* call object.
        
        this is so Fake knows which one to alter
        """
        return self._calls[len(self._calls)-1]
    
    def reset(self):
        self._pointer = 0
    
    def __call__(self, *args, **kw):
        try:
            current_call = self._calls[self._pointer]
        except IndexError:
            raise AssertionError(
                "This attribute of %s can only be called %s time(s).  "
                "Call reset() if necessary or fudge.clear_calls()." % (
                                                self.fake, len(self._calls)))
        self._pointer += 1
        return current_call(*args, **kw)

class Fake(object):
    """A fake object that replaces a real one while testing.

    Most calls with a few exceptions return ``self`` so that you can chain
    them together to create readable code.
    
    Instance methods will raise either AssertionError or :class:`fudge.FakeDeclarationError`

    Keyword arguments:

    **name=None**
        Name of the class, module, or function you mean to replace. If not
        specified, Fake() will try to guess the name by inspecting the calling
        frame (if possible).

    **allows_any_call=False**
        This is **deprecated**.  Use :meth:`Fake:is_a_stub()` instead.

    **callable=False**
        This is **deprecated**.  Use :meth:`Fake.is_callable` instead.

    **expect_call=True**
        This is **deprecated**.  Use :meth:`Fake.expects_call` instead.
        
    """
    
    def __init__(self, name=None, allows_any_call=False,
                 callable=False, expect_call=False):
        self._attributes = {}
        self._declared_calls = {}
        self._name = (name or self._guess_name())
        self._last_declared_call_name = None
        self._is_a_stub = False
        if allows_any_call:
            warnings.warn('Fake(allows_any_call=True) is deprecated;'
                          ' use Fake.is_a_stub()')
            self.is_a_stub()
        self._call_stack = None
        if expect_call:
            self.expects_call()
        elif callable or allows_any_call:
            self.is_callable()
        else:
            self._callable = None
        self._expected_call_order = None

    def __getattribute__(self, name):
        """Favors stubbed out attributes, falls back to real attributes
        
        """
        # this getter circumvents infinite loops:
        def g(n):
            return object.__getattribute__(self, n)
            
        if name in g('_declared_calls'):
            # if it's a call that has been declared
            # as that of the real object then hand it over:
            return g('_declared_calls')[name]
        elif name in g('_attributes'):
            # return attribute declared on real object
            return g('_attributes')[name]
        else:
            # otherwise, first check if it's a call
            # of Fake itself (i.e. returns(),  with_args(), etc)
            try:
                self_call = g(name)
            except AttributeError:
                pass
            else:
                return self_call
            
            if g('_is_a_stub'):
                # Lazily create a attribute (which might later get called):
                stub = Fake(name=self._endpoint_name(name)).is_a_stub()
                self.has_attr(**{name: stub})
                return getattr(self, name)

            raise AttributeError(
                    "%s object does not allow call or attribute '%s' "
                    "(maybe you want %s.is_a_stub() ?)" % (
                                    self, name, self.__class__.__name__))
    
    def __call__(self, *args, **kwargs):
        if '__init__' in self._declared_calls:
            # special case, simulation of __init__():
            call = self._declared_calls['__init__']
            result = call(*args, **kwargs)
            if result is None:
                # assume more calls were expected / provided by the same fake
                return self
            else:
                # a new custom object has been declared
                return result
        elif self._callable:
            return self._callable(*args, **kwargs)
        elif self._is_a_stub:
            self.is_callable().returns_fake().is_a_stub()
            return self.__call__(*args, **kwargs)
        else:
            raise RuntimeError(
                "%s object cannot be called (maybe you want "
                "%s.is_callable() ?)" % (self, self.__class__.__name__))

    def __setattr__(self, name, val):
        if hasattr(self, '_attributes') and name in self._attributes:
            self._attributes[name] = val
        else:
            object.__setattr__(self, name, val)

    def __repr__(self):
        return "fake:%s" % (self._name or "unnamed")
    
    def _declare_call(self, call_name, call):
        self._declared_calls[call_name] = call
    
    _assignment = re.compile(r"\s*(?P<name>[a-zA-Z0-9_]+)\s*=\s*(fudge\.)?Fake\(.*")    
    def _guess_asn_from_file(self, frame):
        if frame.f_code.co_filename:
            if os.path.exists(frame.f_code.co_filename):
                cofile = open(frame.f_code.co_filename,'r')
                try:
                    for ln, line in enumerate(cofile):
                        # I'm not sure why -1 is needed
                        if ln==frame.f_lineno-1:
                            possible_asn = line
                            m = self._assignment.match(possible_asn)
                            if m:
                                return m.group('name')
                finally:
                    cofile.close()
    
    def _guess_name(self):
        if not hasattr(sys, '_getframe'):
            # Stackless?
            return None
        if sys.platform.startswith('java'):
            # frame objects are completely different,
            # not worth the hassle.
            return None
        
        # get frame where class was instantiated,
        #   my_obj = Fake()
        #   ^
        #   we want to set self._name = 'my_obj'
        frame = sys._getframe(2)
        if len(frame.f_code.co_varnames):
            # at the top-most frame:
            co_names = frame.f_code.co_varnames
        else:
            # any other frame:
            co_names = frame.f_code.co_names
        
        # find names that are not locals.
        # this probably indicates my_obj = ...
        
        candidates = [n for n in co_names if n not in frame.f_locals]
        if len(candidates)==0:
            # the value was possibly queued for deref
            #   foo = 44
            #   foo = Fake()
            return self._guess_asn_from_file(frame)
        elif len(candidates)==1:
            return candidates[0]
        else:
            # we are possibly halfway through a module
            # where not all names have been compiled
            return self._guess_asn_from_file(frame)
    
    def _get_current_call(self):
        if not self._last_declared_call_name:
            if not self._callable:
                raise FakeDeclarationError(
                    "Call to a method that expects a predefined call but no such call exists.  "
                    "Maybe you forgot expects('method') or provides('method') ?")
            return self._callable.get_call_object()
        exp = self._declared_calls[self._last_declared_call_name].get_call_object()
        return exp

    def _endpoint_name(self, endpoint):
        p = [self._name or 'unnamed']
        if endpoint != self._name:
            p.append(str(endpoint))
        return '.'.join(p)

    def expects_call(self):
        """The fake must be called.
    
        .. doctest::
            :hide:
        
            >>> import fudge
            >>> fudge.clear_expectations()
            >>> fudge.clear_calls()

        This is useful for when you stub out a function
        as opposed to a class.  For example::

            >>> import fudge
            >>> remove = fudge.Fake('os.remove').expects_call()
            >>> fudge.verify()
            Traceback (most recent call last):
            ...
            AssertionError: fake:os.remove() was not called
    
        .. doctest::
            :hide:
        
            >>> fudge.clear_expectations()
        
        """
        self._callable = ExpectedCall(self, call_name=self._name,
                                      callable=True)
        return self

    def is_callable(self):
        """The fake can be called.

        This is useful for when you stub out a function
        as opposed to a class.  For example::

            >>> import fudge
            >>> remove = Fake('os.remove').is_callable()
            >>> remove('some/path')

        """
        self._callable = Call(self, call_name=self._name, callable=True)
        return self

    def is_a_stub(self):
        """Turns this fake into a stub.

        When a stub, any method is allowed to be called on the Fake() instance
        and any attribute can be accessed.  When an unknown attribute or
        call is made, a new Fake() is returned.  You can of course override
        any of this with :meth:`Fake.expects` and the other methods.
        """
        self._is_a_stub = True
        return self

    def calls(self, call):
        """Redefine a call.
        
        The fake method will execute your function.  I.E.::
            
            >>> f = Fake().provides('hello').calls(lambda: 'Why, hello there')
            >>> f.hello()
            'Why, hello there'
            
        """
        exp = self._get_current_call()
        exp.call_replacement = call
        return self
    
    def expects(self, call_name):
        """Expect a call.
    
        .. doctest::
            :hide:
            
            >>> import fudge
            >>> fudge.clear_expectations()
            >>> fudge.clear_calls()
        
        If the method *call_name* is never called, then raise an error.  I.E.::
            
            >>> session = Fake('session').expects('open').expects('close')
            >>> session.open()
            >>> fudge.verify()
            Traceback (most recent call last):
            ...
            AssertionError: fake:session.close() was not called
        
        .. note:: 
            If you want to also verify the order these calls are made in, 
            use :func:`fudge.Fake.remember_order`.  When using :func:`fudge.Fake.next_call` 
            after ``expects(...)``, each new call will be part of the expected order
        
        Declaring ``expects()`` multiple times is the same as 
        declaring :func:`fudge.Fake.next_call`
        """
        if call_name in self._declared_calls:
            return self.next_call(for_method=call_name)
                        
        self._last_declared_call_name = call_name
        c = ExpectedCall(self, call_name, call_order=self._expected_call_order)
        self._declare_call(call_name, c)
        return self
    
    def has_attr(self, **attributes):
        """Sets available attributes.
        
        I.E.::
            
            >>> User = Fake('User').provides('__init__').has_attr(name='Harry')
            >>> user = User()
            >>> user.name
            'Harry'
            
        """
        self._attributes.update(attributes)
        return self
    
    def next_call(self, for_method=None):
        """Start expecting or providing multiple calls.
        
        .. note:: next_call() cannot be used in combination with :func:`fudge.Fake.times_called`
        
        Up until calling this method, calls are infinite.
        
        For example, before next_call() ... ::
            
            >>> from fudge import Fake
            >>> f = Fake().provides('status').returns('Awake!')
            >>> f.status()
            'Awake!'
            >>> f.status()
            'Awake!'
        
        After next_call() ... ::
            
            >>> from fudge import Fake
            >>> f = Fake().provides('status').returns('Awake!')
            >>> f = f.next_call().returns('Asleep')
            >>> f = f.next_call().returns('Dreaming')
            >>> f.status()
            'Awake!'
            >>> f.status()
            'Asleep'
            >>> f.status()
            'Dreaming'
            >>> f.status()
            Traceback (most recent call last):
            ...
            AssertionError: This attribute of fake:unnamed can only be called 3 time(s).  Call reset() if necessary or fudge.clear_calls().
        
        If you need to affect the next call of something other than the last declared call, 
        use ``next_call(for_method="other_call")``.  Here is an example using getters and setters 
        on a session object ::
            
            >>> from fudge import Fake
            >>> sess = Fake('session').provides('get_count').returns(1)
            >>> sess = sess.provides('set_count').with_args(5)
        
        Now go back and adjust return values for get_count() ::
        
            >>> sess = sess.next_call(for_method='get_count').returns(5)
        
        This allows these calls to be made ::
        
            >>> sess.get_count()
            1
            >>> sess.set_count(5)
            >>> sess.get_count()
            5
        
        When using :func:`fudge.Fake.remember_order` in combination with :func:`fudge.Fake.expects` and :func:`fudge.Fake.next_call` each new call will be part of the expected order.
        
        """
        last_call_name = self._last_declared_call_name
        if for_method:
            if for_method not in self._declared_calls:
                raise FakeDeclarationError(
                            "next_call(for_method=%r) is not possible; "
                            "declare expects(%r) or provides(%r) first" % (
                                                        for_method, for_method, for_method))
            else:
                # set this for the local function:
                last_call_name = for_method
                # reset this for subsequent methods:
                self._last_declared_call_name = last_call_name
                
        if last_call_name:
            exp = self._declared_calls[last_call_name]
        elif self._callable:
            exp = self._callable
        else:
            raise FakeDeclarationError('next_call() must follow provides(), '
                                       'expects() or is_callable()')

        if getattr(exp, 'expected_times_called', None) is not None:
            raise FakeDeclarationError("Cannot use next_call() in combination with times_called()")
        
        if not isinstance(exp, CallStack):
            # lazily create a stack with the last defined 
            # expected call as the first on the stack:
            stack = CallStack(self, initial_calls=[exp], 
                                    expected=isinstance(exp, ExpectedCall),
                                    call_name=exp.call_name)
        
            # replace the old call obj using the same name:
            if last_call_name:
                self._declare_call(last_call_name, stack)
            elif self._callable:
                self._callable = stack
        else:
            stack = exp
        
        # hmm, we need a copy here so that the last call 
        # falls off the stack.
        if stack.expected:
            next_call = ExpectedCall(self, call_name=exp.call_name, call_order=self._expected_call_order)
        else:
            next_call = Call(self, call_name=exp.call_name)
        stack.add_call(next_call)
        return self
    
    def provides(self, call_name):
        """Provide a call.
        
        The call acts as a stub -- no error is raised if it is not called.::
        
            >>> session = Fake('session').provides('open').provides('close')
            >>> import fudge
            >>> fudge.clear_expectations() # from any previously declared fakes
            >>> fudge.clear_calls()
            >>> session.open()
            >>> fudge.verify() # close() not called but no error
        
        Declaring ``provides()`` multiple times is the same as 
        declaring :func:`fudge.Fake.next_call`
            
        """
        if call_name in self._declared_calls:
            return self.next_call(for_method=call_name)
            
        self._last_declared_call_name = call_name
        c = Call(self, call_name)
        self._declare_call(call_name, c)
        return self
    
    def raises(self, exc):
        """Set last call to raise an exception class or instance.
        
        For example::
            
            >>> import fudge
            >>> db = fudge.Fake('db').provides('insert').raises(ValueError("not enough parameters for insert"))
            >>> db.insert()
            Traceback (most recent call last):
            ...
            ValueError: not enough parameters for insert
            
        """
        exp = self._get_current_call()
        exp.exception_to_raise = exc
        return self
    
    def remember_order(self):
        """Verify that subsequent :func:`fudge.Fake.expects` are called in the right order.
        
        For example::
            
            >>> import fudge
            >>> db = fudge.Fake('db').remember_order().expects('insert').expects('update')
            >>> db.update()
            Traceback (most recent call last):
            ...
            AssertionError: Call #1 was fake:db.update(); Expected: #1 fake:db.insert(), #2 fake:db.update(), end
            >>> fudge.clear_expectations()
        
        When declaring multiple calls using :func:`fudge.Fake.next_call`, each subsequent call will be added 
        to the expected order of calls ::
            
            >>> import fudge
            >>> sess = fudge.Fake("session").remember_order().expects("get_id").returns(1)
            >>> sess = sess.expects("set_id").with_args(5)
            >>> sess = sess.next_call(for_method="get_id").returns(5)
        
        Multiple calls to ``get_id()`` are now expected ::
        
            >>> sess.get_id()
            1
            >>> sess.set_id(5)
            >>> sess.get_id()
            5
            >>> fudge.verify()
            >>> fudge.clear_expectations()
        
        """
        if self._callable:
            raise FakeDeclarationError(
                    "remember_order() cannot be used for Fake(callable=True) or Fake(expect_call=True)")
        self._expected_call_order = ExpectedCallOrder(self)
        registry.remember_expected_call_order(self._expected_call_order)
        return self
    
    def returns(self, val):
        """Set the last call to return a value.
        
        Set a static value to return when a method is called.  I.E.::
        
            >>> f = Fake().provides('get_number').returns(64)
            >>> f.get_number()
            64
            
        """
        exp = self._get_current_call()
        exp.return_val = val
        return self
    
    def returns_fake(self, *args, **kwargs):
        """Set the last call to return a new :class:`fudge.Fake`.
        
        Any given arguments are passed to the :class:`fudge.Fake` constructor
        
        Take note that this is different from the cascading nature of 
        other methods.  This will return an instance of the *new* Fake, 
        not self, so you should be careful to store its return value in a new 
        variable.
        
        I.E.::
            
            >>> session = Fake('session')
            >>> query = session.provides('query').returns_fake(name="Query")
            >>> assert query is not session
            >>> query = query.provides('one').returns(['object'])
            
            >>> session.query().one()
            ['object']
            
        """
        exp = self._get_current_call()
        endpoint = kwargs.get('name', exp.call_name)
        name = self._endpoint_name(endpoint)
        kwargs['name'] = '%s()' % name
        fake = self.__class__(*args, **kwargs)
        exp.return_val = fake
        return fake
        
    def times_called(self, n):
        """Set the number of times an object can be called.

        When working with provided calls, you'll only see an 
        error if the expected call count is exceeded ::
        
            >>> auth = Fake('auth').provides('login').times_called(1)
            >>> auth.login()
            >>> auth.login()
            Traceback (most recent call last):
            ...
            AssertionError: fake:auth.login() was called 2 time(s). Expected 1.
        
        When working with expected calls, you'll see an error if 
        the call count is never met ::
        
            >>> import fudge
            >>> auth = fudge.Fake('auth').expects('login').times_called(2)
            >>> auth.login()
            >>> fudge.verify()
            Traceback (most recent call last):
            ...
            AssertionError: fake:auth.login() was called 1 time(s). Expected 2.
        
        .. note:: This cannot be used in combination with :func:`fudge.Fake.next_call`
        
        """
        if self._last_declared_call_name:
            actual_last_call = self._declared_calls[self._last_declared_call_name]
            if isinstance(actual_last_call, CallStack):
                raise FakeDeclarationError("Cannot use times_called() in combination with next_call()")
        # else: # self._callable is in effect
        
        exp = self._get_current_call()
        exp.expected_times_called = n
        return self
    
    def with_args(self, *args, **kwargs):
        """Set the last call to expect specific argument values.
        
        The app under test must send all declared arguments and keyword arguments
        otherwise your test will raise an AssertionError.  For example:
        
        .. doctest::
            
            >>> import fudge
            >>> counter = fudge.Fake('counter').expects('increment').with_args(25, table='hits')
            >>> counter.increment(24, table='clicks')
            Traceback (most recent call last):
            ...
            AssertionError: fake:counter.increment(25, table='hits') was called unexpectedly with args (24, table='clicks')
        
        If you need to work with dynamic argument values 
        consider using :func:`fudge.Fake.with_matching_args` to make looser declarations.
        You can also use :mod:`fudge.inspector` functions.  Here is an example of providing 
        a more flexible ``with_args()`` declaration using inspectors:
        
        .. doctest::
            :hide:
            
            >>> fudge.clear_expectations()
        
        .. doctest::
            
            >>> import fudge
            >>> from fudge.inspector import arg
            >>> counter = fudge.Fake('counter')
            >>> counter = counter.expects('increment').with_args(
            ...                                         arg.any(), 
            ...                                         table=arg.endswith("hits"))
            ... 
        
        The above declaration would allow you to call counter like this:
        
        .. doctest::
            
            >>> counter.increment(999, table="image_hits")
            >>> fudge.verify()
        
        .. doctest::
            :hide:
            
            >>> fudge.clear_calls()
        
        Or like this:
        
        .. doctest::
            
            >>> counter.increment(22, table="user_profile_hits")
            >>> fudge.verify()
            
        .. doctest::
            :hide:
            
            >>> fudge.clear_expectations()
            
        """
        exp = self._get_current_call()
        if args:
            exp.expected_args = args
        if kwargs:
            exp.expected_kwargs = kwargs
        return self
    
    def with_matching_args(self, *args, **kwargs):
        """Set the last call to expect specific argument values if those arguments exist.
        
        Unlike :func:`fudge.Fake.with_args` use this if you want to only declare 
        expectations about matching arguments.  Any unknown keyword arguments 
        used by the app under test will be allowed. 
        
        For example, you can declare positional arguments but ignore keyword arguments:
        
        .. doctest::
            
            >>> import fudge
            >>> db = fudge.Fake('db').expects('transaction').with_matching_args('insert')
        
        With this declaration, any keyword argument is allowed:
        
        .. doctest::
        
            >>> db.transaction('insert', isolation_level='lock')
            >>> db.transaction('insert', isolation_level='shared')
            >>> db.transaction('insert', retry_on_error=True)
            
        .. doctest::
            :hide:
            
            >>> fudge.clear_expectations()
        
        .. note:: 
        
            you may get more mileage out of :mod:`fudge.inspector` functions as 
            described in :func:`fudge.Fake.with_args`
            
        """
        exp = self._get_current_call()
        if args:
            exp.expected_matching_args = args
        if kwargs:
            exp.expected_matching_kwargs = kwargs
        return self
    
    def with_arg_count(self, count):
        """Set the last call to expect an exact argument count.
        
        I.E.::
            
            >>> auth = Fake('auth').provides('login').with_arg_count(2)
            >>> auth.login('joe_user') # forgot password
            Traceback (most recent call last):
            ...
            AssertionError: fake:auth.login() was called with 1 arg(s) but expected 2
            
        """
        exp = self._get_current_call()
        exp.expected_arg_count = count
        return self
    
    def with_kwarg_count(self, count):
        """Set the last call to expect an exact count of keyword arguments.
        
        I.E.::
            
            >>> auth = Fake('auth').provides('login').with_kwarg_count(2)
            >>> auth.login(username='joe') # forgot password=
            Traceback (most recent call last):
            ...
            AssertionError: fake:auth.login() was called with 1 keyword arg(s) but expected 2
            
        """
        exp = self._get_current_call()
        exp.expected_kwarg_count = count
        return self
