from testutils import init, Qit
init()

from qit import Range, Variable, Int, Vector, Function
from qit.base.exception import QitException
import pytest

def test_range_invalid_arg():
    with pytest.raises(QitException):
        Range("fff")

    x = Variable(Vector(Int()), "x")
    with pytest.raises(QitException):
        Range(x)

def test_inconsistent_variables():
    x1 = Variable(Int(), "x")
    x2 = Variable(Int() * Int(), "x")

    with pytest.raises(QitException):
        Function().reads(x1, x2)

def test_unbound_variables():
    ctx = Qit()
    x = Variable(Int(), "x")
    with pytest.raises(QitException):
        ctx.run(Range(x).iterate())

def test_error_function_call():
    ctx = Qit()
    f = Function().takes(Int(), "x").returns(Int())

    with pytest.raises(QitException):
        ctx.run(Range(f("ff")))
