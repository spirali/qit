from testutils import Qit, init
init()

from qit import Bool, Variable

def test_bool_variable():
    ctx = Qit()
    x = Variable(Bool(), "x")

    result = ctx.run(x, args={"x": True})
    assert result is True

    result = ctx.run(x, args={"x": False})
    assert result is False

