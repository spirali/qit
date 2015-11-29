from testutils import Qit, init
init()

from qit import Int, Range, Sequence, System
from qit import Function, Product, Vector, Variable
import itertools

def test_system_empty():
    s = System((Int() * Int()).values(), ())
    result = Qit().run(s.iterate_states(10))
    assert result == []

def test_system_inifinite_initeal_states():
    ctx = Qit()
    r = Range(10).generate()
    s = System(r, ())
    result = ctx.run(s.iterate_states(10).take(30))
    assert len(result) == 30
    assert all(0 <= i < 10 for i in result)

def test_system_basic():
    ctx = Qit()

    # Rules
    f = Function("f").takes(Int(), "x").returns(Int()).code("return x * 10;")
    g = Function("g").takes(Int(), "x").returns(Vector(Int()))
    g.code("if(x % 2 == 0) return {}; else return { x + 1, x + 2 };")
    h = Function("h").takes(Int(), "x").returns(Int()).code("return -x;")

    # Initial states
    v = Int().values(10, 21)

    # System
    s = System(v, (f, g, h))

    result = ctx.run(s.iterate_states(2).sort())
    expected = [-210, # 21, f, h
                -100, # 10, f, h
                -23,  # 21, g, h
                -22,  # 21, g, h
                -21,  # 21, h
                -20,  # 20, h, g
                -19,  # 20, h, g
                -10,  # 10, h
                 10,  # 10
                 21,  # 21
                 22,  # 21, g
                 23,  # 21, g
                 24,  # 21, g, g
                 25,  # 21, g, g
                 100, # 10, f
                 210, # 21, f
                 220, # 21, g, f
                 230, # 21, g, f
                 1000,# 10, f, f
                 2100,# 21, f, f
                ]
    assert result == expected

def test_system_in_product():
    ctx = Qit()
    f = Function("f").takes(Int(), "x").returns(Int()).code("return x * 10;")
    g = Function("g").takes(Int(), "x").returns(Vector(Int())).code("return { x + 1, x + 2 };")

    v = Int().values(10, 20)
    s = System(v, (f,g))

    #i = Int().iterator = s.iterate_states(2)
    P = Product((Int(), "x"), (Int(), "y"))
    P.set_iterator("x", s.iterate_states(2))
    P.set_iterator("y", s.iterate_states(2))

    values = ctx.run(s.iterate_states(2).take(1000))
    pairs = set(itertools.product(values, values))
    result = ctx.run(P.iterate().take(1000))
    assert pairs == set(result)
    assert len(result) == 484


def test_system_rule_variable():
    ctx = Qit()
    x = Variable(Int(), "x")
    f = Function("f").takes(Int(), "a").returns(Int()).reads(x).code("return x;")
    s = System(Int().values(5), (f,))
    result = ctx.run(s.iterate_states(3), args={"x": 5})
    assert result == [5]
