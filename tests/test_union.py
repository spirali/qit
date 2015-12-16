from testutils import Qit, init
init()

from qit import Union, Int, Vector, Set, Map, Function

def test_union_same_types():
    ctx = Qit()
    u = Union(A=Int(), B=Int())
    assert ctx.run(u.value(("A", 12))) == ("A", 12)

def test_union_different_types():
    ctx = Qit()
    a = Int()
    b = Int() * Int()
    c = Vector(b)
    d = Set(a)
    e = Map(b, c)
    u = Union(A=a, B=b, C=c, D=d, E=e, G=None)
    assert ctx.run(u.value(("B", (25, 16)))) == ("B", (25, 16))
    assert ctx.run(u.value(("C", [(25, 16), (3, -2)]))) == ("C", [(25, 16), (3, -2)])
    assert ctx.run(u.value(("G", None))) == ("G", None)

def test_union_all_empty():
    ctx = Qit()
    u = Union(A=None, B=None)
    assert ctx.run(u.value(("A", None))) == ("A", None)
    assert ctx.run(u.value(("B", None))) == ("B", None)

def test_union_api():
    ctx = Qit()
    u = Union(A=None, B=Vector(Int()))
    s = u * u
    f = Function().takes(s, "s").returns(
        Vector(Int())).code("""
            if (s.v1.tag() == B) {
                return s.v1.getB();
            } else {
                return std::vector<int>();
            }""")
    assert ctx.run(f(s.value((("A", None), ("B", [2,3,4]))))) == [2,3,4]

def test_union_sort():
    ctx = Qit()
    u = Union(A=Int(), B=None, C=Int())
    v = (("A", 10), ("B", None), ("C", 5), ("B", None), ("C", 5), ("A", 0), ("A", 20))
    values = u.values(*v)
    result = ctx.run(values.iterate().sort())
    assert result == sorted(v)

def test_union_int_value():
    ctx = Qit()
    u = Union((Int(), Int(), Vector(Int())))
    assert (0, 12) == ctx.run(u.value((0, 12)))
    assert (2, [2,3,4]) == ctx.run(u.value((2, [2,3,4])))
