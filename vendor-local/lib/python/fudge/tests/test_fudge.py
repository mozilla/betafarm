from __future__ import with_statement
import sys
import unittest

from nose.tools import eq_, raises
from nose.exc import SkipTest

import fudge
from fudge.inspector import arg
from fudge import (
    Fake, Registry, ExpectedCall, ExpectedCallOrder, Call, CallStack, FakeDeclarationError)

def test_decorator_on_def():
    class holder:
        test_called = False
    
    bobby = fudge.Fake()
    bobby.expects("suzie_called")
    
    @raises(AssertionError)
    @fudge.with_fakes
    def some_test():
        holder.test_called = True
    
    eq_(some_test.__name__, 'some_test')
    some_test()
    
    eq_(holder.test_called, True)

# for a test below
_some_fake = fudge.Fake()

class TestFake(unittest.TestCase):
    
    def test_guess_name(self):
        if sys.platform.startswith('java'):
            raise SkipTest("not supported")
        my_obj = fudge.Fake()
        eq_(repr(my_obj), "fake:my_obj")
        
    def test_guess_name_globals(self):
        if sys.platform.startswith('java'):
            raise SkipTest("not supported")
        eq_(repr(_some_fake), "fake:_some_fake")
        
    def test_guess_name_deref(self):
        if sys.platform.startswith('java'):
            raise SkipTest("not supported")
        my_obj = 44
        my_obj = fudge.Fake()
        eq_(repr(my_obj), "fake:my_obj")
    
    def test_has_attr(self):
        my_obj = fudge.Fake().has_attr(vice='versa', beach='playa')
        eq_(my_obj.vice, 'versa')
        eq_(my_obj.beach, 'playa')

    def test_attributes_are_settable(self):
        my_obj = fudge.Fake().has_attr(vice='versa')
        my_obj.vice = 'miami'
        eq_(my_obj.vice, 'miami')

    def test_none_type_attributes_are_settable(self):
        my_obj = fudge.Fake().has_attr(vice=None)
        eq_(my_obj.vice, None)
        my_obj.vice = 'miami'
        eq_(my_obj.vice, 'miami')

    def test_attributes_can_replace_internals(self):
        my_obj = fudge.Fake().has_attr(provides='hijacked')
        eq_(my_obj.provides, 'hijacked')
    
    def test_repr_shortens_long_values(self):
        fake = Fake("widget").provides("set_bits").with_args(
            "12345678910111213141516171819202122232425262728293031"
        )
        try:
            fake.set_bits()
        except AssertionError, exc:
            eq_(str(exc),
            "fake:widget.set_bits('123456789101112131415161718192021222324252627...') "
            "was called unexpectedly with args ()")
        else:
            raise RuntimeError("expected AssertionError")


class TestChainedNames(unittest.TestCase):

    def setUp(self):
        self.fake = fudge.Fake('db.Adapter')
    
    def tearDown(self):
        fudge.clear_expectations()

    def test_basic(self):
        eq_(repr(self.fake), 'fake:db.Adapter')

    def test_nesting(self):
        f = self.fake
        f = f.provides('query').returns_fake().provides('fetchall')
        eq_(repr(f), 'fake:db.Adapter.query()')
        f = f.provides('cursor').returns_fake()
        eq_(repr(f), 'fake:db.Adapter.query().cursor()')

    def test_more_nesting(self):
        class ctx:
            fake = None
        @fudge.patch('smtplib.SMTP')
        def test(fake_SMTP):
            (fake_SMTP.is_callable()
             .returns_fake()
             .provides('sendmail'))
            ctx.fake = fake_SMTP()
        test()
        eq_(str(ctx.fake), 'fake:smtplib.SMTP()')


class TestIsAStub(unittest.TestCase):
    
    def tearDown(self):
        fudge.clear_expectations()

    def test_is_callable(self):
        f = fudge.Fake().is_a_stub()
        result = f()
        assert isinstance(result, fudge.Fake)

    def test_infinite_callables(self):
        f = fudge.Fake().is_a_stub()
        result = f()()()
        assert isinstance(result, fudge.Fake)

    def test_is_any_call(self):
        f = fudge.Fake().is_a_stub()
        assert isinstance(f.foobar(), fudge.Fake)
        assert isinstance(f.foozilated(), fudge.Fake)

    def test_is_any_call_with_any_args(self):
        f = fudge.Fake().is_a_stub()
        assert isinstance(f.foobar(blazz='Blaz', kudoz='Klazzed'),
                          fudge.Fake)

    def test_stubs_are_infinite(self):
        f = fudge.Fake().is_a_stub()
        assert isinstance(f.one().two().three(), fudge.Fake)

    def test_stubs_have_any_attribute(self):
        f = fudge.Fake().is_a_stub()
        assert isinstance(f.foo, fudge.Fake)
        assert isinstance(f.bar, fudge.Fake)

    def test_attributes_are_infinite(self):
        f = fudge.Fake().is_a_stub()
        assert isinstance(f.foo.bar.barfoo, fudge.Fake)

    def test_infinite_path_expectation(self):
        f = fudge.Fake().is_a_stub()
        f.foo.bar().expects('barfoo')
        f.foo.bar().barfoo()

    @raises(AssertionError)
    def test_infinite_path_expectation_is_verified(self):
        f = fudge.Fake().is_a_stub()
        f.foo.bar().expects('barfoo').with_args(foo='bar')
        f.foo.bar().barfoo()
        fudge.verify()

    def test_infinite_path_naming(self):
        f = fudge.Fake(name='base').is_a_stub()
        eq_(str(f.foo.bar().baz), 'fake:base.foo.bar().baz')


class TestLongArgValues(unittest.TestCase):
    
    def test_arg_diffs_are_not_shortened(self):
        fake = Fake("widget").provides("set_bits").with_args(
            "12345678910111213141516171819202122232425262728293031"
        )
        try:
            # this should not be shortened but the above arg spec should:
            fake.set_bits("99999999999999999999999999999999999999999999999999999999")
        except AssertionError, exc:
            eq_(str(exc),
            "fake:widget.set_bits('123456789101112131415161718192021222324252627...') "
            "was called unexpectedly with args "
            "('99999999999999999999999999999999999999999999999999999999')")
        else:
            raise RuntimeError("expected AssertionError")
    
    def test_kwarg_diffs_are_not_shortened(self):
        fake = Fake("widget").provides("set_bits").with_args(
            newbits="12345678910111213141516171819202122232425262728293031"
        )
        try:
            # this should not be shortened but the above arg spec should:
            fake.set_bits(newbits="99999999999999999999999999999999999999999999999999999999")
        except AssertionError, exc:
            eq_(str(exc),
            "fake:widget.set_bits(newbits='123456789101112131415161718192021222324252627...') "
            "was called unexpectedly with args "
            "(newbits='99999999999999999999999999999999999999999999999999999999')")
        else:
            raise RuntimeError("expected AssertionError")

class TestArguments(unittest.TestCase):
    
    def setUp(self):
        self.fake = fudge.Fake()
    
    def tearDown(self):
        fudge.clear_expectations()
    
    @raises(AssertionError)
    def test_wrong_args(self):
        exp = self.fake.expects('theCall').with_args(
                        1, 
                        "ho ho ho ho ho ho ho, it's Santa", 
                        {'ditto':False})
        exp.theCall()
        
    @raises(AssertionError)
    def test_wrong_kwargs(self):
        exp = self.fake.expects('other').with_args(one="twozy", items=[1,2,3,4])
        exp.other(nice="NOT NICE")
        
    @raises(AssertionError)
    def test_arg_count(self):
        exp = self.fake.expects('one').with_arg_count(3)
        exp.one('no', 'maybe')
        
    @raises(AssertionError)
    def test_kwarg_count(self):
        exp = self.fake.expects('__init__').with_kwarg_count(2)
        exp(maybe="yes, maybe")
    
    @raises(FakeDeclarationError)
    def test_with_args_requires_a_method(self):
        self.fake.with_args('something')
    
    @raises(AssertionError)
    def test_with_args_can_operate_on_provision(self):
        self.fake.provides("not_expected").with_args('something')
        self.fake.not_expected() # should still raise arg error
    
    @raises(AssertionError)
    def test_with_args_checks_args(self):
        self.fake.expects('count').with_args('one', two='two')
        self.fake.count(two='two')
        
    @raises(AssertionError)
    def test_with_args_checks_kwargs(self):
        self.fake.expects('count').with_args('one', two='two')
        self.fake.count('one')

    @raises(AssertionError)
    def test_raises_does_not_obscure_with_kwargs(self):
        # previously, this test failed because the raises(exc) 
        # was raised too early.  Issue 6
        self.fake.expects('count').with_args(two='two').raises(RuntimeError('bork'))
        self.fake.count('one') # wrong kwargs

    @raises(AssertionError)
    def test_raises_does_not_obscure_with_args(self):
        # Issue 6
        self.fake.expects('count').with_args('one').raises(RuntimeError('bork'))
        self.fake.count(two='two') # wrong args
    
    @raises(AssertionError)
    def test_too_many_args(self):
        db = Fake("db").expects("execute").with_args(bind={'one':1})
        db.execute("select foozilate()", bind={'one':1}) # unexpected statement arg
    
    def test_zero_keywords_ok(self):
        mail = fudge.Fake('mail').expects('send').with_arg_count(3) 
        mail.send("you", "me", "hi") # no kw args should be ok
    
    def test_zero_args_ok(self):
        mail = fudge.Fake('mail').expects('send').with_kwarg_count(3) 
        mail.send(to="you", from_="me", msg="hi") # no args should be ok
        
    def test_with_args_with_object_that_is_never_equal_to_anything(self):
        class NeverEqual(object):
            def __eq__(self, other):
                return False
        obj = NeverEqual()
        self.fake.expects('save').with_args(arg.any())
        self.fake.save(obj) # this should pass but was failing prior to issue 9

    def test_with_kwargs_with_object_that_is_never_equal_to_anything(self):
        class NeverEqual(object):
            def __eq__(self, other):
                return False
        obj = NeverEqual()
        self.fake.expects('save').with_args(foo=arg.any())
        self.fake.save(foo=obj) # this should pass but was failing prior to issue 9
    
    def test_with_matching_positional_args(self):
        db = self.fake
        db.expects('transaction').with_matching_args('insert')
        db.transaction("insert", isolation_level="lock")
        fudge.verify()
    
    def test_with_matching_keyword_args(self):
        db = self.fake
        db.expects('transaction').with_matching_args(isolation_level="lock")
        db.transaction("insert", isolation_level="lock")
        fudge.verify()
    
    @raises(AssertionError)
    def test_with_non_matching_positional_args(self):
        db = self.fake
        db.expects('transaction').with_matching_args('update')
        db.transaction("insert", isolation_level="lock")
        fudge.verify()
    
    @raises(AssertionError)
    def test_with_too_many_non_matching_positional_args(self):
        # this may be unintuitve but specifying too many 
        # arguments constitutes as non-matching.  Why?  
        # Because how else is it possible to implement, by index?
        db = self.fake
        db.expects('transaction').with_matching_args('update')
        db.transaction("update", "delete", isolation_level="lock")
        fudge.verify()
    
    @raises(AssertionError)
    def test_with_non_matching_keyword_args(self):
        db = self.fake
        db.expects('transaction').with_matching_args(isolation_level="read")
        db.transaction("insert", isolation_level="lock")
        fudge.verify()
    
    @raises(AssertionError)
    def test_missing_matching_positional_args_is_not_ok(self):
        # this is awkward to implement so I think it should not be supported
        db = self.fake
        db.expects('transaction').with_matching_args("update")
        db.transaction()
        fudge.verify()
    
    def test_missing_matching_keyword_args_is_ok(self):
        db = self.fake
        db.expects('transaction').with_matching_args(isolation_level="read")
        db.transaction()
        fudge.verify()

## hmm, arg diffing needs more thought

# class TestArgDiff(unittest.TestCase):
#     
#     def setUp(self):
#         self.fake = Fake("foo")
#         self.call = Call(self.fake)
#     
#     def test_empty(self):
#         eq_(self.call._arg_diff(tuple(), tuple()), "")
#     
#     def test_one_unexpected(self):
#         eq_(self.call._arg_diff(('one',), tuple()), "arg #1 was unexpected")
#     
#     def test_one_missing(self):
#         eq_(self.call._arg_diff(tuple(), ('one',)), "arg #1 never showed up")
#     
#     def test_four_unexpected(self):
#         eq_(self.call._arg_diff(
#             ('one','two','three','four'),
#             ('one','two','three')), "arg #4 was unexpected")
#     
#     def test_four_missing(self):
#         eq_(self.call._arg_diff(
#             ('one','two','three'), 
#             ('one','two','three','four')), "arg #4 never showed up")
#     
#     def test_one_mismatch(self):
#         eq_(self.call._arg_diff(('won',), ('one',)), "arg #1 'won' != 'one'")
#     
#     def test_four_mismatch(self):
#         eq_(self.call._arg_diff(
#             ('one','two','three','not four'), 
#             ('one','two','three','four')), "arg #4 'not four' != 'four'")

# class TestKeywordArgDiff(unittest.TestCase):
#     
#     def setUp(self):
#         self.fake = Fake("foo")
#         self.call = Call(self.fake)
#     
#     def test_empty(self):
#         eq_(self.call._keyword_diff({}, {}), (True, ""))
#     
#     def test_one_empty(self):
#         eq_(self.call._keyword_diff({}, 
#             {'something':'here','another':'there'}), 
#             (False, "these keywords never showed up: ('something', 'another')"))
#     
#     def test_complex_match_yields_no_reason(self):
#         actual = {'num':1, 'two':2, 'three':3}
#         expected = {'num':1, 'two':2, 'three':3}
#         eq_(self.call._keyword_diff(actual, expected), (True, ""))
#     
#     def test_simple_mismatch_yields_no_reason(self):
#         actual = {'num':1}
#         expected = {'num':2}
#         eq_(self.call._keyword_diff(actual, expected), (False, ""))
#     
#     def test_simple_match_yields_no_reason(self):
#         actual = {'num':1}
#         expected = {'num':1}
#         eq_(self.call._keyword_diff(actual, expected), (True, ""))
#     
#     def test_actual_kw_extra_key(self):
#         actual = {'one':1, 'two':2}
#         expected = {'one':1}
#         eq_(self.call._keyword_diff(actual, expected), 
#             (False, "keyword 'two' was not expected"))
#     
#     def test_actual_kw_value_inequal(self):
#         actual = {'one':1, 'two':2}
#         expected = {'one':1, 'two':3}
#         eq_(self.call._keyword_diff(actual, expected), 
#             (False, "two=2 != two=3"))
#     
#     def test_expected_kw_extra_key(self):
#         actual = {'one':1}
#         expected = {'one':1, 'two':2}
#         eq_(self.call._keyword_diff(actual, expected), 
#             (False, "this keyword never showed up: ('two',)"))
#     
#     def test_expected_kw_value_inequal(self):
#         actual = {'one':1, 'two':'not two'}
#         expected = {'one':1, 'two':2}
#         eq_(self.call._keyword_diff(actual, expected), 
#             (False, "two='not two' != two=2"))

class TestCall(unittest.TestCase):
    
    def setUp(self):
        self.fake = fudge.Fake('SMTP')
    
    def test_repr(self):
        s = Call(self.fake)
        eq_(repr(s), "fake:SMTP()")
    
    def test_repr_callable(self):
        s = Call(self.fake.is_callable())
        eq_(repr(s), "fake:SMTP()")
    
    def test_repr_with_args(self):
        s = Call(self.fake)
        s.expected_args = [1,"bad"]
        eq_(repr(s), "fake:SMTP(1, 'bad')")
    
    def test_repr_with_kwargs(self):
        s = Call(self.fake)
        s.expected_args = [1,"bad"]
        s.expected_kwargs = {'baz':'borzo'}
        eq_(repr(s), "fake:SMTP(1, 'bad', baz='borzo')")
    
    def test_named_repr_with_args(self):
        s = Call(self.fake, call_name='connect')
        s.expected_args = [1,"bad"]
        eq_(repr(s), "fake:SMTP.connect(1, 'bad')")
    
    def test_nested_named_repr_with_args(self):
        f = self.fake.provides('get_conn').returns_fake()
        s = Call(f, call_name='connect')
        s.expected_args = [1,"bad"]
        eq_(repr(s), "fake:SMTP.get_conn().connect(1, 'bad')")
    
    def test_named_repr_with_index(self):
        s = Call(self.fake, call_name='connect')
        s.expected_args = [1,"bad"]
        s.index = 0
        eq_(repr(s), "fake:SMTP.connect(1, 'bad')[0]")
        s.index = 1
        eq_(repr(s), "fake:SMTP.connect(1, 'bad')[1]")
        

class TestCallStack(unittest.TestCase):
    
    def setUp(self):
        self.fake = fudge.Fake('SMTP')
    
    def test_calls(self):
        call_stack = CallStack(self.fake)
        
        c = Call(self.fake)
        c.return_val = 1
        call_stack.add_call(c)
        
        c = Call(self.fake)
        c.return_val = 2
        call_stack.add_call(c)
        
        eq_(call_stack(), 1)
        eq_(call_stack(), 2)
    
    @raises(AssertionError)
    def test_no_calls(self):
        call_stack = CallStack(self.fake)
        call_stack()
    
    @raises(AssertionError)
    def test_end_of_calls(self):
        call_stack = CallStack(self.fake)
        
        c = Call(self.fake)
        c.return_val = 1
        call_stack.add_call(c)
        
        eq_(call_stack(), 1)
        call_stack()
    
    def test_get_call_object(self):
        call_stack = CallStack(self.fake)
        
        c = Call(self.fake)
        call_stack.add_call(c)
        
        assert call_stack.get_call_object() is c
        
        d = Call(self.fake)
        call_stack.add_call(d)
        
        assert call_stack.get_call_object() is d
    
    def test_with_initial_calls(self):
        c = Call(self.fake)
        c.return_val = 1
        call_stack = CallStack(self.fake, initial_calls=[c])
        
        eq_(call_stack(), 1)
    
    def test_reset(self):
        call_stack = CallStack(self.fake)
        
        c = Call(self.fake)
        c.return_val = 1
        call_stack.add_call(c)
        
        c = Call(self.fake)
        c.return_val = 2
        call_stack.add_call(c)
        
        eq_(call_stack(), 1)
        eq_(call_stack(), 2)
        
        call_stack.reset()
        
        eq_(call_stack(), 1)
        eq_(call_stack(), 2)
        
class TestFakeCallables(unittest.TestCase):
    
    def tearDown(self):
        fudge.clear_expectations()
    
    @raises(RuntimeError)
    def test_not_callable_by_default(self):
        self.fake = fudge.Fake()
        self.fake()
    
    def test_callable(self):
        fake = fudge.Fake().is_callable()
        fake() # allow the call
        fudge.verify() # no error
    
    @raises(AttributeError)
    def test_cannot_stub_any_call_by_default(self):
        self.fake.Anything() # must define this first
    
    @raises(AssertionError)
    def test_stub_with_args(self):
        self.fake = fudge.Fake().is_callable().with_args(1,2)
        self.fake(1)
    
    @raises(AssertionError)
    def test_stub_with_arg_count(self):
        self.fake = fudge.Fake().is_callable().with_arg_count(3)
        self.fake('bah')
    
    @raises(AssertionError)
    def test_stub_with_kwarg_count(self):
        self.fake = fudge.Fake().is_callable().with_kwarg_count(3)
        self.fake(two=1)
    
    def test_stub_with_provides(self):
        self.fake = fudge.Fake().provides("something")
        self.fake.something()
    
    def test_fake_can_sabotage_itself(self):
        # I'm not sure if there should be a warning 
        # for this but it seems that it should be 
        # possible for maximum flexibility:
        
        # replace Fake.with_args()
        self.fake = fudge.Fake().provides("with_args").returns(1)
        eq_(self.fake.with_args(), 1)
    
    @raises(AssertionError)
    def test_stub_with_provides_and_args(self):
        self.fake = fudge.Fake().provides("something").with_args(1,2)
        self.fake.something()
    
    def test_stub_is_not_registered(self):
        self.fake = fudge.Fake().provides("something")
        exp = self.fake._get_current_call()
        eq_(exp.call_name, "something")
        assert exp not in fudge.registry
    
    @raises(RuntimeError)
    def test_raises_class(self):
        self.fake = fudge.Fake().provides("fail").raises(RuntimeError)
        self.fake.fail()
    
    @raises(RuntimeError)
    def test_raises_instance(self):
        self.fake = fudge.Fake().provides("fail").raises(RuntimeError("batteries ran out"))
        self.fake.fail()

class TestReplacementCalls(unittest.TestCase):
    
    def tearDown(self):
        fudge.clear_expectations()
    
    def test_replace_call(self):
        
        def something():
            return "hijacked"
            
        fake = fudge.Fake().provides("something").calls(something)
        eq_(fake.something(), "hijacked")
    
    def test_calls_mixed_with_returns(self):
        
        called = []
        def something():
            called.append(True)
            return "hijacked"
            
        fake = fudge.Fake().provides("something").calls(something).returns("other")
        eq_(fake.something(), "other")
        eq_(called, [True])
    
    @raises(AssertionError)
    def test_calls_mixed_with_expectations(self):
        
        def something():
            return "hijacked"
        
        # with_args() expectation should not get lost:
        fake = fudge.Fake().provides("something").calls(something).with_args(1,2)
        eq_(fake.something(), "hijacked")
    
    def test_replace_init(self):
        
        class custom_object:
            def hello(self):
                return "hi"
            
        fake = fudge.Fake().provides("__init__").returns(custom_object())
        eq_(fake().hello(), "hi")
        
class TestFakeTimesCalled(unittest.TestCase):
    
    def tearDown(self):
        fudge.clear_expectations()
        
    def test_when_provided(self):
        self.fake = fudge.Fake().provides("something").times_called(2)
        # this should not raise an error because the call was provided not expected
        fudge.verify()
        
    @raises(AssertionError)
    def test_when_provided_raises_on_too_many_calls(self):
        self.fake = fudge.Fake().provides("something").times_called(2)
        self.fake.something()
        self.fake.something()
        self.fake.something() # too many
    
    @raises(AssertionError)
    def test_when_expected(self):
        self.fake = fudge.Fake().expects("something").times_called(2)
        self.fake.something()
        fudge.verify()
    
    @raises(AssertionError)
    def test_when_expected_raises_on_too_many_calls(self):
        self.fake = fudge.Fake().expects("something").times_called(2)
        self.fake.something()
        self.fake.something()
        self.fake.something() # too many
        fudge.verify()
        
    @raises(AssertionError)
    def test_expected_callable(self):
        login = fudge.Fake('login',expect_call=True).times_called(2)
        login()
        fudge.verify()
        
    def test_callable_ok(self):
        self.fake = fudge.Fake(callable=True).times_called(2)
        self.fake()
        self.fake()
        fudge.verify()
        
    def test_when_provided_ok(self):
        self.fake = fudge.Fake().provides("something").times_called(2)
        self.fake.something()
        self.fake.something()
        fudge.verify()
        
    def test_when_expected_ok(self):
        self.fake = fudge.Fake().expects("something").times_called(2)
        self.fake.something()
        self.fake.something()
        fudge.verify()

class TestNextCall(unittest.TestCase):
    
    def tearDown(self):
        fudge.clear_expectations()
    
    @raises(FakeDeclarationError)
    def test_next_call_then_times_called_is_error(self):
        self.fake = fudge.Fake().expects("hi").returns("goodday").next_call().times_called(4)
        self.fake.hi()
        self.fake.hi()
        fudge.verify()
    
    @raises(FakeDeclarationError)
    def test_times_called_then_next_call_is_error(self):
        self.fake = fudge.Fake().expects("hi").times_called(4).next_call()
        self.fake.hi()
        self.fake.hi()
        fudge.verify()
            
    def test_stacked_returns(self):
        fake = fudge.Fake().provides("something")
        fake = fake.returns(1)
        fake = fake.next_call()
        fake = fake.returns(2)
        fake = fake.next_call()
        fake = fake.returns(3)
        
        eq_(fake.something(), 1)
        eq_(fake.something(), 2)
        eq_(fake.something(), 3)
    
    @raises(AssertionError)
    def test_stacked_calls_are_finite(self):
        self.fake = fudge.Fake().provides("something")
        self.fake = self.fake.returns(1)
        self.fake = self.fake.next_call()
        self.fake = self.fake.returns(2)
        
        eq_(self.fake.something(), 1)
        eq_(self.fake.something(), 2)
        self.fake.something()
        
    def test_stack_is_reset_when_name_changes(self):
        self.fake = fudge.Fake().provides("something")
        self.fake = self.fake.returns(1)
        self.fake = self.fake.next_call()
        self.fake = self.fake.returns(2)
        self.fake = self.fake.provides("other")
        self.fake = self.fake.returns(3)
        
        eq_(self.fake.something(), 1)
        eq_(self.fake.something(), 2)
        eq_(self.fake.other(), 3)
        eq_(self.fake.other(), 3)
        eq_(self.fake.other(), 3)
        eq_(self.fake.other(), 3)
        eq_(self.fake.other(), 3)
        
    def test_next_call_with_multiple_returns(self):
        self.fake = fudge.Fake().provides("something")
        self.fake = self.fake.returns(1)
        self.fake = self.fake.next_call()
        self.fake = self.fake.returns(2)
        self.fake = self.fake.provides("other")
        self.fake = self.fake.returns(3)
        self.fake = self.fake.next_call()
        self.fake = self.fake.returns(4)
        
        eq_(self.fake.something(), 1)
        eq_(self.fake.something(), 2)
        eq_(self.fake.other(), 3)
        eq_(self.fake.other(), 4)
    
    def test_stacked_calls_do_not_collide(self):
        self.fake = fudge.Fake().provides("something")
        self.fake = self.fake.returns(1)
        self.fake = self.fake.next_call()
        self.fake = self.fake.returns(2)
        self.fake = self.fake.provides("other")
        self.fake = self.fake.returns(3)
        self.fake = self.fake.next_call()
        self.fake = self.fake.returns(4)
        
        eq_(self.fake.something(), 1)
        eq_(self.fake.other(), 3)
        eq_(self.fake.something(), 2)
        eq_(self.fake.other(), 4)
    
    def test_returns_are_infinite(self):
        self.fake = fudge.Fake().provides("something").returns(1)
        
        eq_(self.fake.something(), 1)
        eq_(self.fake.something(), 1)
        eq_(self.fake.something(), 1)
        eq_(self.fake.something(), 1)
        eq_(self.fake.something(), 1)
        eq_(self.fake.something(), 1)
        eq_(self.fake.something(), 1)
        eq_(self.fake.something(), 1)
        
    def test_stacked_does_not_copy_expectations(self):
        
        fake = fudge.Fake().expects("add")
        fake = fake.with_args(1,2).returns(3)
        
        fake = fake.next_call()
        fake = fake.returns(-1)
        
        eq_(fake.add(1,2), 3)
        eq_(fake.add(), -1)
        
    def test_stacked_calls_are_in_registry(self):
        fake = fudge.Fake().expects("count").with_args(1)
        fake = fake.next_call().with_args(2)
        fake = fake.next_call().with_args(3)
        fake = fake.next_call().with_args(4)
        
        # hmm
        call_stack = fake._declared_calls[fake._last_declared_call_name]
        calls = [c for c in call_stack]
        assert calls[0] in fudge.registry
        assert calls[1] in fudge.registry
        assert calls[2] in fudge.registry
        assert calls[3] in fudge.registry
        
    def test_stacked_calls_are_indexed(self):
        fake = fudge.Fake().expects("count").with_args(1)
        fake = fake.next_call().with_args(2)
        fake = fake.next_call().with_args(3)
        fake = fake.next_call().with_args(4)
        
        # hmm
        call_stack = fake._declared_calls[fake._last_declared_call_name]
        calls = [c for c in call_stack]
        eq_(calls[0].index, 0)
        eq_(calls[1].index, 1)
        eq_(calls[2].index, 2)
        eq_(calls[3].index, 3)
    
    def test_start_stop_resets_stack(self):
        fudge.clear_expectations()
        fake = fudge.Fake().provides("something")
        fake = fake.returns(1)
        fake = fake.next_call()
        fake = fake.returns(2)
        
        eq_(fake.something(), 1)
        eq_(fake.something(), 2)
        
        fudge.clear_calls()
        
        eq_(fake.something(), 1)
        eq_(fake.something(), 2)
        
        fudge.verify()
        
        eq_(fake.something(), 1)
        eq_(fake.something(), 2)
    
    def test_next_call_with_callables(self):
        login = (fudge.Fake('login')
                                .is_callable()
                                .returns("yes")
                                .next_call()
                                .returns("maybe")
                                .next_call()
                                .returns("no"))
        eq_(login(), "yes")
        eq_(login(), "maybe")
        eq_(login(), "no")
    
    def test_returns(self):
        db = Fake("db")\
            .provides("get_id").returns(1)\
            .provides("set_id")\
            .next_call(for_method="get_id").returns(2)
        # print [c.return_val for c in db._declared_calls["get_id"]._calls]
        eq_(db.get_id(), 1)
        eq_(db.set_id(), None)
        eq_(db.get_id(), 2)
    
    def test_expectations_with_multiple_return_values(self):
        db = Fake("db")\
            .expects("get_id").returns(1)\
            .expects("set_id")\
            .next_call(for_method="get_id").returns(2)
        eq_(db.get_id(), 1)
        eq_(db.set_id(), None)
        eq_(db.get_id(), 2)
        
        fudge.verify()


class TestExpectsAndProvides(unittest.TestCase):
    
    def tearDown(self):
        fudge.clear_expectations()
    
    @raises(AssertionError)
    def test_nocall(self):
        fake = fudge.Fake()
        exp = fake.expects('something')
        fudge.verify()
        
    def test_multiple_provides_on_chained_fakes_ok(self):
        db = Fake("db").provides("insert").returns_fake().provides("insert")
        
    def test_multiple_expects_on_chained_fakes_ok(self):
        db = Fake("db").expects("insert").returns_fake().expects("insert")
        
    def test_callable_expectation(self):
        fake_setup = fudge.Fake('setup', expect_call=True)
        fake_setup()
        # was called so verification should pass:
        fudge.verify()
        
    def test_callable_expectation_with_args(self):
        fake_setup = (fudge.Fake('setup', expect_call=True)
                            .with_args('<db>'))
        fake_setup('<db>')
        # was called so verification should pass:
        fudge.verify()
        
    def test_multiple_expects_act_like_next_call(self):
        self.fake = fudge.Fake().expects("something")
        self.fake = self.fake.returns(1)
        self.fake = self.fake.expects("something")
        self.fake = self.fake.returns(2)
        
        eq_(self.fake.something(), 1)
        eq_(self.fake.something(), 2)
        
    def test_multiple_provides_act_like_next_call(self):
        self.fake = fudge.Fake().provides("something")
        self.fake = self.fake.returns(1)
        self.fake = self.fake.provides("something")
        self.fake = self.fake.returns(2)
        
        eq_(self.fake.something(), 1)
        eq_(self.fake.something(), 2)
        
    def test_multiple_expects_for_sep_methods(self):
        self.fake = (fudge.Fake()
                        .expects("marco")
                        .returns(1)
                        .expects("polo")
                        .returns('A')
                        .expects("marco")
                        .returns(2)
                        .expects("polo")
                        .returns('B')
        )
        
        eq_(self.fake.marco(), 1)
        eq_(self.fake.marco(), 2)
        eq_(self.fake.polo(), 'A')
        eq_(self.fake.polo(), 'B')
        
    def test_multiple_provides_for_sep_methods(self):
        self.fake = (fudge.Fake()
                        .provides("marco")
                        .returns(1)
                        .provides("polo")
                        .returns('A')
                        .provides("marco")
                        .returns(2)
                        .provides("polo")
                        .returns('B')
        )
        
        eq_(self.fake.marco(), 1)
        eq_(self.fake.marco(), 2)
        eq_(self.fake.polo(), 'A')
        eq_(self.fake.polo(), 'B')

class TestOrderedCalls(unittest.TestCase):
    
    def tearDown(self):
        fudge.clear_expectations()
    
    @raises(AssertionError)
    def test_out_of_order(self):
        fake = fudge.Fake().remember_order().expects("one").expects("two")
        fake.two()
        fake.one()
        fudge.verify()
    
    @raises(FakeDeclarationError)
    def test_cannot_remember_order_when_callable_is_true(self):
        fake = fudge.Fake().is_callable().remember_order()
    
    @raises(FakeDeclarationError)
    def test_cannot_remember_order_when_expect_call_is_true(self):
        fake = fudge.Fake(expect_call=True).remember_order()
    
    @raises(AssertionError)
    def test_not_enough_calls(self):
        # need to drop down a level to bypass expected calls:
        r = Registry()
        fake = Fake()
        call_order = ExpectedCallOrder(fake)
        r.remember_expected_call_order(call_order)
        
        exp = ExpectedCall(fake, "callMe", call_order=call_order)
        call_order.add_expected_call(exp)
        
        r.verify()
        
    @raises(AssertionError)
    def test_only_one_call(self):
        # need to drop down a level to bypass expected calls:
        r = Registry()
        fake = Fake()
        call_order = ExpectedCallOrder(fake)
        r.remember_expected_call_order(call_order)
        
        exp = ExpectedCall(fake, "one", call_order=call_order)
        call_order.add_expected_call(exp)
        exp() # call this
        
        exp = ExpectedCall(fake, "two", call_order=call_order)
        call_order.add_expected_call(exp)
        
        r.verify()
        
    def test_incremental_order_assertion_ok(self):
        # need to drop down a level to bypass expected calls:
        fake = Fake()
        call_order = ExpectedCallOrder(fake)
        
        exp = ExpectedCall(fake, "one", call_order=call_order)
        call_order.add_expected_call(exp)
        exp() # call this
        
        exp = ExpectedCall(fake, "two", call_order=call_order)
        call_order.add_expected_call(exp)
        
        # two() not called but assertion is not finalized:
        call_order.assert_order_met(finalize=False)
    
    def test_multiple_returns_affect_order(self):
        db = Fake("db")\
            .remember_order()\
            .expects("get_id").returns(1)\
            .expects("set_id")\
            .next_call(for_method="get_id").returns(2)
        eq_(db.get_id(), 1)
        eq_(db.set_id(), None)
        eq_(db.get_id(), 2)
        fudge.verify()
    
    @raises(AssertionError)
    def test_chained_fakes_honor_order(self):
        Thing = Fake("thing").remember_order().expects("__init__")
        holder = Thing.expects("get_holder").returns_fake()
        holder = holder.expects("init")
        
        thing = Thing()
        holder = thing.get_holder()
        # missing thing.init()
        fudge.verify()
    
    @raises(AssertionError)
    def test_too_many_calls(self):
        db = Fake("db")\
            .remember_order()\
            .expects("get_id").returns(1)\
            .expects("set_id")
        eq_(db.get_id(), 1)
        eq_(db.set_id(), None)
        # extra :
        eq_(db.get_id(), 1)

    @raises(AssertionError)
    def test_expects_call_shortcut(self):
        remove = Fake("os.remove").expects_call()
        fudge.verify()
        assert isinstance(remove, Fake)

    def test_expects_call_shortcut_ok(self):
        remove = Fake("os.remove").expects_call()
        remove()
        fudge.verify()
        assert isinstance(remove, Fake)

    def test_provides_call_shortcut(self):
        remove = Fake("os.remove").is_callable()
        remove()
        assert isinstance(remove, Fake)


class TestPatchedFakes(unittest.TestCase):
    
    def tearDown(self):
        fudge.clear_expectations()

    def test_expectations_are_cleared(self):

        class holder:
            test_called = False

        # Set up decoy expectation:
        fake = fudge.Fake('db').expects('save')

        @fudge.patch('shutil.copy')
        def some_test(copy):
            holder.test_called = True

        some_test()
        fudge.verify() # should be no errors
        eq_(holder.test_called, True)

    def test_expectations_are_verified(self):

        class holder:
            test_called = False
        
        @raises(AssertionError)
        @fudge.patch('shutil.copy')
        def some_test(copy):
            copy.expects('__call__')
            holder.test_called = True
        
        some_test()
        eq_(holder.test_called, True)

    def test_expectations_are_always_cleared(self):

        class holder:
            test_called = False
        
        @raises(RuntimeError)
        @fudge.patch('shutil.copy')
        def some_test(copy):
            holder.test_called = True
            copy.expects_call()
            raise RuntimeError

        some_test()
        fudge.verify() # should be no errors
        eq_(holder.test_called, True)

    def test_calls_are_cleared(self):

        class holder:
            test_called = False

        sess = fudge.Fake('session').expects('save')
        # call should be cleared:
        sess.save()

        @fudge.patch('shutil.copy')
        def some_test(copy):
            holder.test_called = True
            copy.expects_call().times_called(1)
            copy()

        some_test()
        fudge.verify() # should be no errors
        eq_(holder.test_called, True)

    def test_with_statement(self):

        class holder:
            test_called = False
        
        @raises(AssertionError)
        def run_test():
            with fudge.patch('shutil.copy') as copy:
                copy.expects('__call__')
                holder.test_called = True
        
        run_test()
        eq_(holder.test_called, True)

    def test_with_statement_exception(self):

        @raises(RuntimeError)
        def run_test():
            with fudge.patch('shutil.copy') as copy:
                copy.expects('__call__')
                raise RuntimeError()

        run_test()


class TestNonPatchedFakeTest(unittest.TestCase):
    
    def tearDown(self):
        fudge.clear_expectations()

    def test_preserve_method(self):

        @fudge.test
        def some_test():
            holder.test_called = True

        eq_(some_test.__name__, 'some_test')

    def test_expectations_are_cleared(self):

        class holder:
            test_called = False

        # Set up decoy expectation:
        fake = fudge.Fake('db').expects('save')

        @fudge.test
        def some_test():
            holder.test_called = True

        some_test()
        fudge.verify() # should be no errors
        eq_(holder.test_called, True)

    def test_expectations_are_always_cleared(self):

        class holder:
            test_called = False
        
        @raises(RuntimeError)
        @fudge.test
        def some_test():
            holder.test_called = True
            fake = fudge.Fake('db').expects('save')
            raise RuntimeError

        some_test()
        fudge.verify() # should be no errors
        eq_(holder.test_called, True)

    def test_calls_are_cleared(self):

        class holder:
            test_called = False

        sess = fudge.Fake('session').expects('save')
        # call should be cleared:
        sess.save()

        @fudge.test
        def some_test():
            holder.test_called = True
            db = fudge.Fake('db').expects('save').times_called(1)
            db.save()

        some_test()
        fudge.verify() # should be no errors
        eq_(holder.test_called, True)

    @raises(AssertionError)
    def test_verify(self):

        @fudge.test
        def some_test():
            fake = fudge.Fake('db').expects('save')

        some_test()
