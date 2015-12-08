from testutils import Qit, init
init()

from qit import Enum, Variable

def test_enum_variable():
    ctx = Qit()
    x = Variable(Enum("A", "B"), "x")
    assert ctx.run(x, args={"x": "A"}) == "A"

def test_enum_value():
    ctx = Qit()
    assert ctx.run(Enum("Xxx", "Zzz", "A2B").value("Zzz")) == "Zzz"
