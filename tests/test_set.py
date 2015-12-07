from testutils import Qit, init
init()

from qit import Int, Struct, Set

def test_set_constructor():
    ctx = Qit()
    s = Struct(Int(), Int())
    v = Set(s)
    result = ctx.run(v.value({(10, 11), (20, 21)}))
    assert result == {(10, 11), (20, 21)}

