from testutils import Qit, init
init()

import pytest

from qit import Range, Function, Int, KeyValue, Struct
from qit.functions.int import add
from qit.base.exception import ProgramCrashed

def test_iterator_first_no_default():
    ctx = Qit()
    fn = Function().takes(Int(), "a").returns(Int()).code("return a > 100;")
    result =  ctx.run(Range(91, 120, 2).iterate().filter(fn).first())
    assert result == 101
    with pytest.raises(ProgramCrashed):
        ctx.run(Range(10, 20, 2).iterate().filter(fn).first())

def test_iterator_first_default_value():
    ctx = Qit()
    fn = Function().takes(Int(), "a").returns(Int()).code("return a > 100;")
    result =  ctx.run(Range(91, 120, 2).iterate().filter(fn).first(111))
    assert result == 101
    result = ctx.run(Range(10, 20, 2).iterate().filter(fn).first(111))
    assert result == 111

def test_iterator_first_maybe():
    ctx = Qit()
    fn = Function().takes(Int(), "a").returns(Int()).code("return a > 100;")
    result =  ctx.run(Range(91, 120, 2).iterate().filter(fn).first_maybe())
    assert result == ("Just", 101)
    result = ctx.run(Range(10, 20, 2).iterate().filter(fn).first_maybe())
    assert result == ("Nothing", None)

def test_iterator_is_empty():
    ctx = Qit()
    fn = Function().takes(Int(), "a").returns(Int()).code("return a > 100;")
    assert not ctx.run(Range(91, 120, 2).iterate().filter(fn).is_empty())
    assert ctx.run(Range(10, 20, 2).iterate().filter(fn).is_empty())

def test_iterator_is_nonempty():
    ctx = Qit()
    fn = Function().takes(Int(), "a").returns(Int()).code("return a > 100;")
    assert ctx.run(Range(91, 120, 2).iterate().filter(fn).is_nonempty())
    assert not ctx.run(Range(10, 20, 2).iterate().filter(fn).is_nonempty())

def test_reduce():
    ctx = Qit()
    result = ctx.run(Int().values(12, 13, 7, 0, 5).iterate().reduce(add))
    assert result == 37
    result = ctx.run(Int().values(12).iterate().reduce(add))
    assert result == 12

def test_reduce_keyval():
    ctx = Qit()
    kv = KeyValue(Int(), Int())
    values = ((12, 3), (17, 1), (5, 0), (12, 4), (2, 0))
    a = kv.values(*values).iterate().reduce(kv.max_fn)
    b = kv.values(*values).iterate().reduce(kv.min_fn)
    result = ctx.run((Struct(kv, kv)).value((a, b)))
    assert ((12, 4), (5, 0)) == result
