from testutils import Qit, init
init()

from qit import Int, Vector, Function
from qit.base.exception import QitException
import pytest

def test_run_more_values():
    ctx = Qit()
    v = Vector(Int())
    a, b, c = ctx.run(Int().value(1),
                      Int().value(2),
                      v.value([1,2,3]))
    assert a == 1
    assert b == 2
    assert c == [1,2,3]

def test_run_variables_in_variables():
    ctx = Qit()

    x = Int().variable("x")
    y = Int().variable("y")
    a = Int().variable("a")
    b = Int().variable("b")
    c = Int().variable("c")

    f = Function().returns(Int()).reads(x).code("return x;")
    g = Function().returns(Int()).reads(c).code("return c;")

    result = ctx.run(a, args = {
        x : y,
        y : 123,
        a : f(),
        b : g(),
        c : c
    })

    assert result == 123

def test_run_circular_deps():
    ctx = Qit()

    x = Int().variable("x")
    y = Int().variable("y")

    with pytest.raises(QitException):
        ctx.run(x, args = {
            x : y,
            y : x,
        })


