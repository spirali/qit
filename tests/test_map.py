from testutils import Qit, init
init()

from qit import Int, Variable, Map, Function, Struct

def test_map_value():
    ctx = Qit()
    m = { 1: 1, 2: 2, 3: 3 }
    assert ctx.run(Map(Int(), Int()).value(m)) == m

    m = { (1, 2) : (2, 1), (3, 4): (4, 3), (5, 6): (6, 5) }
    s = Struct(Int(), Int())
    assert ctx.run(Map(s, s).value(m)) == m

def test_map_variable():
    ctx = Qit()
    m = Variable(Map(Int(), Int()), "m")
    assert ctx.run(m, args={m: { 2: 1, 1: 2 }}) == { 2: 1, 1: 2 }

    m = Map(Int(), Int() * Int())
    x = Variable(Int(), "x")
    assert ctx.run(m.value({1: (x, 20)}), args={x: 123}) == {1: (123, 20)}

def test_map_function():
    ctx = Qit()
    t = Map(Int(), Int())
    f = Function().takes(t, "input").returns(t).code("""
    // reverse
    std::map<qint, qint > output;
    for (auto rit = input.rbegin(); rit != input.crend(); ++rit) {
        output[rit->first] = rit->second;
    }
    return output;
    """)
    assert ctx.run(f({ 3: 3, 2: 2, 1: 1 })) == { 1: 1, 2: 2, 3: 3 }

def test_map_empty():
    ctx = Qit()
    ctx.run(Map(Int(), Int()).value( {} ))

def test_map_in_map():
    def prepare_map (start, size):
        return dict((start + i, start * i) for i in range(size))

    ctx = Qit()
    d = dict((i, prepare_map(i, 10)) for i in range(3))
    assert ctx.run(Map(Int(), Map(Int(), Int())).value(d)) == d
