from testutils import Qit, init
init()

from qit import Int, Variable, Map, Function, Struct, Bool

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

def test_map_with_own_key_comparator():
    ctx = Qit()
    m = { (1, 1): (1, 2),
          (2, 1): (2, 3),
          (3, 5): (3, 8),
          (4, 7): (4, 11) }
    mtype = Struct((Int(), "x"), (Int(), "y"))
    cmp_keys = Function().takes(mtype, "key1")\
                         .takes(mtype, "key2")\
                         .returns(Bool())
    cmp_keys.code("return key1.x < key2.x;")
    qm = Map(mtype, mtype, cmp_keys)
    assert ctx.run(qm.value(m)) == m

    cmp_keys.code("return key1.y < key2.y;")
    del m[(1, 1)] # this value is replace by (2,1) because of changed function
    assert ctx.run(qm.value(m)) == m

def test_map_with_own_key_comparator2():
    ctx = Qit()
    m = { (1, 1): (1, 2),
          (2, 1): (2, 3),
          (3, 5): (3, 8),
          (4, 7): (4, 11) }

    z = Int().variable("z")
    mtype = Struct((Int(), "x"), (Int(), "y"))
    cmp_keys = Function().takes(mtype, "key1")\
                         .takes(mtype, "key2")\
                         .reads(z)\
                         .returns(Bool())
    cmp_keys.code("return key1.x < key2.x && key1.x <= z;")
    qm = Map(mtype, mtype, cmp_keys)
    assert ctx.run(qm.value(m), args={z: 6}) == m
