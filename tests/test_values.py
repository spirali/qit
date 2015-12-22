from testutils import Qit, init
init()

from qit import Int, Range, Vector, Variable


def test_values_int_empty():
    v = Int().values()
    result = Qit().run(v.iterate())
    assert result == []

def test_values_product_empty():
    v = (Int() * Int()).values()
    result = Qit().run(v.iterate())
    assert result == []

def test_int_values():
    v = Int().values(30, 20, 10)
    result = Qit().run(v.iterate())
    assert result == [ 30, 20, 10 ]

    result = Qit().run(v.generate().take(100))
    for i in result:
        assert i in (30, 20, 10)


def test_product_values():
    ctx = Qit()
    p = Range(4) * Range(10)
    v = p.values((0,0), (1, 7), (3, 2))

    result = ctx.run(v.iterate())
    assert [(0,0), (1, 7), (3, 2)] == result

    result = ctx.run(v.generate().take(100))
    assert all(i in ((0,0), (1, 7), (3, 2)) for i in result)

def test_vector_values():
    ctx = Qit()
    s1 = [(1,2), (3,4), (7,7)]
    s2 = [(1,1), (2, 2)]
    s3 = []
    s4 = [(4,4), (4,4), (4,4)]

    p = Int() * Int()
    s = Vector(p)
    v = s.values(s1, s2, s3, s4)

    result = ctx.run(v.iterate())
    assert result == [ s1, s2, s3, s4 ]

    result = ctx.run(v.generate().take(150))
    assert all(i in [ s1, s2, s3, s4 ] for i in result)

def test_values_int_variable():
    ctx = Qit()
    x = Variable(Int(), "x")
    y = Variable(Int(), "y")

    r = Int().values(x, 7, y)
    result = ctx.run(r.iterate(), args={x: 2, y: 11})
    assert result == [ 2, 7, 11 ]

def test_values_product_variable():
    ctx = Qit()
    x = Variable(Int() * Int(), "x")
    r = (Int() * Int()).values(x, (2,3))
    result = ctx.run(r.iterate(), args={x: (7,5)})
    assert result == [(7,5),(2,3)]
