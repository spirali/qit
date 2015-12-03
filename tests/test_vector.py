from testutils import Qit, init
init()

from qit import Int, Struct, Vector, Variable

def test_vector_constant():
    ctx = Qit()
    s = Struct(Int(), Int())
    v = Vector(s)
    x = Variable(v, "x")
    result = ctx.run(x, args={"x": [(11,12), (5, 2)]})
    assert result == [(11,12), (5, 2)]

