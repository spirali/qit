import pytest
from testutils import Qit, init
init()

from qit import Range, Function, Bool, Int, Product


def test_filter_empty():
    r = Range(5)
    q = Qit()

    f = Function("filter").returns(Bool()).takes(r, "r").code("return false;")

    assert len(q.run(r.iterate().filter(f))) == 0


def test_filter_wrong_return_type():
    q = Qit()
    r = Range(5)

    f = Function("filter").returns(Int()).takes(r, "q").code("return false;")

    with pytest.raises(Exception):
        q.run(r.iterate().filter(f))


def test_filter_even():
    r = Range(5)
    q = Qit()

    f = Function("filter").returns(Bool()).takes(r, "r").code("return r % 2 == 0;")

    assert q.run(r.iterate().filter(f)) == [0, 2, 4]


def test_filter_map():
    r = Range(5)
    q = Qit()

    f = Function("f").returns(Int()).takes(Int(), "r").code("return r * 2;")
    g = Function("g").returns(Bool()).takes(Int(), "x").code("return x == 4;")
    h = Function("h").returns(Int()).takes(Int(), "r").code("return r + 1;")

    q.run(r.iterate().map(f).filter(g).map(h)) == 5


def test_filter_product():
    p = Product("P", (Range(5), "x"), (Range(5), "y"))
    q = Qit()

    f = Function("filter").returns(Bool()).takes(p, "p").code("return p.x == p.y;")

    q.run(p.iterate().filter(f)) == [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
