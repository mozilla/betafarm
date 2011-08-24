
import re
import unittest

from nose.tools import eq_, raises

import fudge
from fudge import inspector
from fudge.inspector import arg
from fudge import Fake

class TestAnyValue(unittest.TestCase):
    
    def tearDown(self):
        fudge.clear_expectations()
    
    def test_any_value(self):
        db = Fake("db").expects("execute").with_args(arg.any())
        db.execute("delete from foo where 1")
    
    def test_repr(self):
        any = inspector.AnyValue()
        eq_(repr(any), "arg.any()")
        
    def test_str(self):
        any = inspector.AnyValue()
        eq_(str(any), "arg.any()")
        
class TestPassesTest(unittest.TestCase):
    
    def tearDown(self):
        fudge.clear_expectations()
    
    def test_passes(self):
        def isint(v):
            return isinstance(v,int)
        counter = Fake("counter").expects("increment").with_args(arg.passes_test(isint))
        counter.increment(25)
    
    @raises(AssertionError)
    def test_passes_fail(self):
        def is_str(v):
            return isinstance(v,str)
        counter = Fake("counter").expects("set_name").with_args(arg.passes_test(is_str))
        counter.set_name(25)
    
    def test_repr(self):
        class test(object):
            def __call__(self, v):
                return isinstance(v,int)
            def __repr__(self):
                return "v is an int"
                
        passes = inspector.PassesTest(test())
        eq_(repr(passes), "arg.passes_test(v is an int)")
    
    def test_str(self):
        class test(object):
            def __call__(self, v):
                return isinstance(v,int)
            def __repr__(self):
                return "v is an int"
                
        passes = inspector.PassesTest(test())
        eq_(str(passes), "arg.passes_test(v is an int)")

class TestObjectlike(unittest.TestCase):
    
    def tearDown(self):
        fudge.clear_expectations()
    
    def test_has_attr_ok(self):
        class Config(object):
            size = 12
            color = 'red'
            weight = 'heavy'
            
        widget = Fake("widget").expects("configure")\
                               .with_args(arg.has_attr(size=12,color='red'))
        widget.configure(Config())
    
    @raises(AssertionError)
    def test_has_attr_fail(self):
        class Config(object):
            color = 'red'
            
        widget = Fake("widget").expects("configure")\
                               .with_args(arg.has_attr(size=12))
        widget.configure(Config())
    
    @raises(AssertionError)
    def test_has_attr_fail_wrong_value(self):
        class Config(object):
            color = 'red'
            
        widget = Fake("widget").expects("configure")\
                               .with_args(arg.has_attr(color="green"))
        widget.configure(Config())
    
    def test_objectlike_str(self):
        o = inspector.HasAttr(one=1, two="two")
        eq_(str(o), "arg.has_attr(one=1, two='two')")
    
    def test_objectlike_repr(self):
        o = inspector.HasAttr(one=1, two="two")
        eq_(repr(o), "arg.has_attr(one=1, two='two')")
    
    def test_objectlike_unicode(self):
        o = inspector.HasAttr(one=1, ivan=u"Ivan_Krsti\u0107")
        assert repr(o).startswith("arg.has_attr(ivan=")
        assert repr(o).endswith("'Ivan_Krsti\u0107', one=1)")
    
    def test_objectlike_repr_long_val(self):
        o = inspector.HasAttr(
                bytes="011110101000101010011111111110000001010100000001110000000011")
        eq_(repr(o), 
            "arg.has_attr(bytes='011110101000101010011111111110000001010100000...')")

class TestStringlike(unittest.TestCase):
    
    def tearDown(self):
        fudge.clear_expectations()
    
    def test_startswith_ok(self):
        db = Fake("db").expects("execute").with_args(arg.startswith("insert into"))
        db.execute("insert into foo values (1,2,3,4)")
    
    @raises(AssertionError)
    def test_startswith_fail(self):
        db = Fake("db").expects("execute").with_args(arg.startswith("insert into"))
        db.execute("select from")
    
    def test_startswith_ok_uni(self):
        db = Fake("db").expects("execute").with_args(arg.startswith(u"Ivan_Krsti\u0107"))
        db.execute(u"Ivan_Krsti\u0107(); foo();")
    
    def test_startswith_unicode(self):
        p = inspector.Startswith(u"Ivan_Krsti\u0107")
        assert repr(p).startswith("arg.startswith(")
        assert repr(p).endswith("'Ivan_Krsti\u0107')")
    
    def test_endswith_ok(self):
        db = Fake("db").expects("execute").with_args(arg.endswith("values (1,2,3,4)"))
        db.execute("insert into foo values (1,2,3,4)")
    
    def test_endswith_ok_uni(self):
        db = Fake("db").expects("execute").with_args(arg.endswith(u"Ivan Krsti\u0107"))
        db.execute(u"select Ivan Krsti\u0107")
        
    def test_endswith_unicode(self):
        p = inspector.Endswith(u"Ivan_Krsti\u0107")
        assert repr(p).startswith("arg.endswith(")
        assert repr(p).endswith("'Ivan_Krsti\u0107')")
    
    def test_startswith_repr(self):
        p = inspector.Startswith("_start")
        eq_(repr(p), "arg.startswith('_start')")
    
    def test_endswith_repr(self):
        p = inspector.Endswith("_ending")
        eq_(repr(p), "arg.endswith('_ending')")
    
    def test_startswith_str(self):
        p = inspector.Startswith("_start")
        eq_(str(p), "arg.startswith('_start')")
    
    def test_endswith_str(self):
        p = inspector.Endswith("_ending")
        eq_(str(p), "arg.endswith('_ending')")
    
    def test_startswith_str_long_value(self):
        p = inspector.Startswith(
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        )
        eq_(str(p), 
            "arg.startswith('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA...')" )
    
    def test_endswith_str_long_value(self):
        p = inspector.Endswith(
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        )
        eq_(str(p), 
            "arg.endswith('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA...')" )

class TestContains(unittest.TestCase):
    
    def tearDown(self):
        fudge.clear_expectations()
    
    def test_contains_str(self):
        db = Fake("db").expects("execute").with_args(arg.contains("table foo"))
        db.execute("select into table foo;")
        db.execute("select * from table foo where bar = 1")
        fudge.verify()
    
    @raises(AssertionError)
    def test_contains_fail(self):
        db = Fake("db").expects("execute").with_args(arg.contains("table foo"))
        db.execute("select into table notyourmama;")
        fudge.verify()
    
    def test_contains_list(self):
        db = Fake("db").expects("execute_statements").with_args(
                                            arg.contains("select * from foo"))
        db.execute_statements([
            "update foo",
            "select * from foo",
            "drop table foo"
        ])
        fudge.verify()
        
    def test_str(self):
        c = inspector.Contains(":part:")
        eq_(str(c), "arg.contains(':part:')")
        
    def test_str_long_val(self):
        c = inspector.Contains(
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        eq_(str(c), "arg.contains('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA...')")
        
    def test_repr(self):
        c = inspector.Contains(":part:")
        eq_(repr(c), "arg.contains(':part:')")
        
    def test_unicode(self):
        c = inspector.Contains(u"Ivan_Krsti\u0107")
        assert repr(c).startswith("arg.contains(")
        assert repr(c).endswith("'Ivan_Krsti\u0107')")
        
        