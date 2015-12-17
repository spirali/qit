from testutils import Qit, init
init()

import pytest

from qit import Range, Function, Int
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
