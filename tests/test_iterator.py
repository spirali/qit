from testutils import Qit, init
init()

from qit import Range, Function, Int

def test_iterator_first():
    ctx = Qit()
    fn = Function().takes(Int(), "a").returns(Int()).code("return a > 100;")
    assert ctx.run(Range(91, 120, 2).iterate().filter(fn).first()) == ("Just", 101)
    assert ctx.run(Range(10, 20, 2).iterate().filter(fn).first()) == ("Nothing", None)

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
