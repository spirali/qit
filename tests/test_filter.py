import pytest
from testutils import Qit, init
init()

from qit import Range, Function, Bool, Int, Product, Variable


def test_filter_empty():
    r = Range(5)
    q = Qit()

    f = Function("filter").returns(Bool()).takes(r.type, "r").code("return false;")

    assert len(q.run(r.iterate().filter(f))) == 0

def test_filter_even():
    r = Range(5)
    q = Qit()

    f = Function("filter").returns(Bool()).takes(r.type, "r").code("return r % 2 == 0;")

    assert q.run(r.iterate().filter(f)) == [0, 2, 4]


def test_filter_map():
    r = Range(5)
    q = Qit()

    f = Function("f").returns(Int()).takes(Int(), "r").code("return r * 2;")
    g = Function("g").returns(Bool()).takes(Int(), "x").code("return x == 4;")
    h = Function("h").returns(Int()).takes(Int(), "r").code("return r + 1;")

    q.run(r.iterate().map(f).filter(g).map(h)) == 5


def test_filter_product():
    p = Product((Range(5), "x"), (Range(5), "y"))
    q = Qit()

    f = Function("filter").returns(Bool()).takes(p.type, "p").code("return p.x == p.y;")

    q.run(p.iterate().filter(f)) == [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]

def test_filter_free_variables():
    ctx = Qit()
    x = Variable(Int(), "x")
    f = Function().takes(Int(), "a").returns(Bool()).reads(x).code("return a != x;")
    result = ctx.run(Range(5).iterate().filter(f), args={"x" : 3})
    assert result == [0, 1, 2, 4]
