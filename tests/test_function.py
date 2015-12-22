from testutils import Qit, init
init()

from qit import Range, Variable, Int, Sequence, Function

def test_function_in_function():
    c = Qit()
    x = Variable(Int(), "x")
    r = Range(x).iterate()
    f = r.make_function()

    r2 = Range(x).iterate().map(f)
    f = r2.make_function((x,))

    r3 = Range(x).iterate().map(f)
    assert [[], [[]], [[], [0]], [[], [0], [0,1]]] == c.run(r3, args={ "x": 4 })


def test_outer_variables():
    c = Qit()
    x = Variable(Int(), "x")
    f = Function().takes(Int(), "a").returns(Int()).reads(x)
    f.code("return a * x;")
    r = Range(x).iterate().map(f)
    assert [0, 5, 10, 15, 20] == c.run(r, args={ "x": 5 })


def test_outer_variables_in_fn_iterator():
    c = Qit()
    x = Variable(Int(), "x")
    y = Variable(Int(), "y")

    plus_1 = Function().takes(Int(), "x").returns(Int()).code("return x + 1;")
    P = Range(plus_1(x)) * Range(y)
    f = P.iterate().to_vector().make_function((x,))

    result = c.run(Range(3).iterate().map(f), args={"y": 2})
    assert [[(0, 0), (0, 1)],
            [(0, 0), (1, 0), (0, 1), (1, 1)],
            [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)]] == result

def test_apply_function_nofree_vars():
    c = Qit()
    x = Variable(Int(), "x")
    y = Variable(Int(), "y")
    f = Function().takes(Int(), "a").returns(Int()).reads(y).code("return a + y;")
    assert [0,1,2,3,4] == c.run(Range(f(x)).iterate(), args={"x": 3, "y": 2})

def test_apply_function_free_vars():
    c = Qit()
    x = Variable(Int(), "x")
    f = Function().takes(Int(), "a").returns(Int()).code("return a + 10;")
    assert list(range(13)) == c.run(Range(f(x)).iterate(), args={"x": 3})

def test_apply_function_constant():
    c = Qit()
    f = Function().takes(Int(), "a").returns(Int()).code("return a + 10;")
    assert list(range(16)) == c.run(Range(f(6)).iterate())

def test_function_constant():
    c = Qit()
    f = Int().value(7).make_function()
    result = c.run(f())
    assert result == 7

def test_function_transport_freevars():
    ctx = Qit()
    x = Int().variable("x")
    f = Function().returns(Int()).code("return {{x}};", x=x)
    g = Function().returns(Int()).code("return {{f}}();", f=f)
    assert 11 == ctx.run(g(), args={"x": 11 })
