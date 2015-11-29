from testutils import Qit, init
init()

from qit import Int, Function, Variable

def test_int_variable():
    ctx = Qit()
    x = Variable(Int(), "x")
    assert ctx.run(x, args={"x": 10}) == 10

def test_int_function():
    ctx = Qit()
    f = Function().takes(Int(), "a").returns(Int()).code("return a + 2;")
    assert ctx.run(f(10)) == 12

def test_int_function_variables():
    ctx = Qit()
    x = Variable(Int(), "x")
    f = Function().takes(Int(), "a").returns(Int()).reads(x).code("return a + x;")
    assert ctx.run(f(10), args={"x": 15}) == 25
