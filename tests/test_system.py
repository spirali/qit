from testutils import Qit, init
init()

from qit import Int, Range, System, Domain
from qit import Function, Product, Vector, Variable
import itertools

def test_system_empty():
    s = System((Int() * Int()).values(), ())
    result = Qit().run(s.states(10).iterate())
    assert result == []

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

    expected = [ (-210, 2), # 21, f, h
                 (-100, 2), # 10, f, h
                 (-23, 2),  # 21, g, h
                 (-22, 2),  # 21, g, h
                 (-21, 1),  # 21, h
                 (-20, 2),  # 20, h, g
                 (-19, 2),  # 20, h, g
                 (-10, 1),  # 10, h
                 (10, 0),  # 10
                 (21, 0),  # 21
                 (22, 1),  # 21, g
                 (23, 1),  # 21, g
                 (24, 2),  # 21, g, g
                 (25, 2),  # 21, g, g
                 (100, 1), # 10, f
                 (210, 1), # 21, f
                 (220, 2), # 21, g, f
                 (230, 2), # 21, g, f
                 (1000, 2), # 10, f, f
                 (2100, 2), # 21, f, f
                ]

    result = ctx.run(s.states(2, return_depth=True).iterate().sort())
    assert result == expected

    result = ctx.run(s.states(2).iterate().sort())
    assert result == [ state for state, depth in expected ]


def test_system_in_product():
    ctx = Qit()
    f = Function("f").takes(Int(), "x").returns(Int()).code("return x * 10;")
    g = Function("g").takes(Int(), "x").returns(Vector(Int())).code("return { x + 1, x + 2 };")

    v = Int().values(10, 20)
    s = System(v, (f,g))

    D = s.states(2)
    P = Product(D, D)

    values = ctx.run(D.iterate().take(1000))
    pairs = set(itertools.product(values, values))
    result = ctx.run(P.iterate().take(1000))
    assert len(result) == 484 # 22 * 22
    assert pairs == set(result)

def test_system_rule_variable():
    ctx = Qit()
    x = Variable(Int(), "x")
    f = Function("f").takes(Int(), "a").returns(Int()).reads(x).code("return x;")
    s = System(Int().values(5), (f,))
    result = ctx.run(s.states(3).iterate(), args={x: 5})
    assert result == [5]
