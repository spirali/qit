from testutils import Qit, init
init()

from qit import Int, Struct, Variable, KeyValue

def test_struct_variable():
    ctx = Qit()
    s = Struct(Int(), Int())
    s2 = Struct(s, Int(), s)
    x = Variable(s2, "x")
    result = ctx.run(x, args={"x": ((11,12), 13, (5, 2))})
    assert result == ((11,12), 13, (5, 2))

def test_struct_mul():
    s1 = Int() * Int()
    s2 = Struct(Int(), Int())
    assert s1 == s2

    s1 = Int() * Int() * Int()
    s2 = Struct(Int(), Int(), Int())
    assert s1 == s2

def test_struct_empty():
    ctx = Qit()
    s1 = Struct()
    ctx.run(s1.value(()))

def test_struct_constructor():
    ctx = Qit()
    x = Variable(Int(), "x")
    s = Int() * Int() * Int()
    result = ctx.run(s.value((x, 10, x)), args={"x": 11})
    assert result == (11, 10, 11)

def test_keyval():
    ctx = Qit()
    kv = KeyValue(Int() * Int(), Int())
    assert ctx.run(kv.key_fn(kv.value(((22, 33), 11)))) == (22, 33)
    assert ctx.run(kv.value_fn(kv.value(((22, 33), 11)))) == 11
