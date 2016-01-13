from testutils import Qit, init
init()

from qit import Int, Range, System, Domain, ActionSystem, Bool
from qit import Function, Product, Vector, Variable, Functor, Values
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

inline_code = """
    if (s1.s1_id != s2.s1_id) {
        return s1.s1_id < s2.s1_id;
    }
    if (s1.action != s2.action) {
        return s1.action < s2.action;
    }
    return s1.s2_id < s2.s2_id;"""

def test_empty_action_system():

    s = ActionSystem(Int().values(1), ())
    result = Qit().run(s.states(10).iterate())
    assert result == []

def test_basic_action_system():
    f = Function("f").takes(Int(), "x").returns(Int()).code("return x + 1;")
    s = ActionSystem(Int().values(1), (f,))
    cmp_system_states = Function().takes(s.sas_type, "s1")\
                                  .takes(s.sas_type, "s2")\
                                  .returns(Bool())
    cmp_system_states.code(inline_code)
    depth = 10
    result = Qit().run(s.states(depth).iterate().sort(cmp_fn=cmp_system_states))
    expected = [(i, 'f', i + 1) for i in range(1, depth + 2)]
    assert result == expected

def test_basic_action_system_depth():
    f = Function("f").takes(Int(), "x").returns(Int()).code("return x + 1;")
    s = ActionSystem(Int().values(1), (f,))
    cmp_system_states = Function().takes(s.sas_type, "s1")\
                                  .takes(s.sas_type, "s2")\
                                  .returns(Bool())
    cmp_system_states.code(inline_code)
    depth = 10
    result = Qit().run(s.states(depth, return_depth=True).iterate())
    expected = [((i, 'f', i + 1), i - 1) for i in range(1, depth + 2)]
    assert result == expected

def test_action_system_two_functions():
    f = Function("f").takes(Int(), "x").returns(Int()).code("return x + 2;")
    g = Function("g").takes(Int(), "x").returns(Int()).code("return x - 1;")

    s = ActionSystem(Int().values(1), (f, g))
    result = Qit().run(s.states(2).iterate())
    assert result == [(1, 'f', 2),
                      (1, 'g', 3),
                      (3, 'f', 4),
                      (3, 'g', 5),
                      (2, 'f', 6),
                      (2, 'g', 4),
                      (6, 'f', 7),
                      (6, 'g', 8),
                      (5, 'f', 1),
                      (5, 'g', 9),
                      (4, 'f', 8),
                      (4, 'g', 1)]

    cmp_system_states = Function().takes(s.sas_type, "s1")\
                                  .takes(s.sas_type, "s2")\
                                  .returns(Bool())
    cmp_system_states.code(inline_code)
    result = Qit().run(s.states(2).iterate().sort(cmp_fn=cmp_system_states))
    assert result == [(1, 'f', 2),
                      (1, 'g', 3),
                      (2, 'f', 6),
                      (2, 'g', 4),
                      (3, 'f', 4),
                      (3, 'g', 5),
                      (4, 'f', 8),
                      (4, 'g', 1),
                      (5, 'f', 1),
                      (5, 'g', 9),
                      (6, 'f', 7),
                      (6, 'g', 8)]

def test_action_system_empty_vector_action():
    empty = Function().takes(Int(), "x").returns(Vector(Int()))
    empty.code("return {};")

    s = ActionSystem(Int().values(1), (empty, ))
    result = Qit().run(s.states(10).iterate())
    assert result == []

def test_action_system_vector_action():
    odd = Function("odd").takes(Int(), "x").returns(Vector(Int())).code("""
        if (x % 2 != 0) {
            return {x, 2*x + 1};
        }
        return {};
    """)

    s = ActionSystem(Int().values(1), (odd, ))
    depth = 5
    result = Qit().run(s.states(depth).iterate())
    expected = list(itertools.chain.from_iterable(
        ((i, "odd", i), (i, "odd", i + 1)) for i in range(1, depth + 2)))
    assert result == expected

def test_action_system_free_variable():
    ctx = Qit()

    f = Function("f").takes(Int(), "x").returns(Int()).code("""
        return x + 1;
    """)

    x = Int().variable("x")
    s = ActionSystem(Values(Int(), [x]), (f, ))
    fs = s.states(2).iterate().make_function((x,))

    g = Function().takes(Int(), "x").returns(Vector(s.sas_type)).code("""
        return {{fs}}(x);
    """, fs=fs)

    r = Range(3)
    res = ctx.run(r.iterate().map(g))
    assert res == [[(i, "f", i + 1) for i in range(1, 4)] for j in range(3)]
