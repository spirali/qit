from testutils import Qit, init
init()

from qit import Int, Range, Sequence

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
    assert all(i in (30, 20, 10) for i in result)


def test_product_values():
    p = Range(4) * Range(10)
    v = p.values((0,0), (1, 7), (3, 2))

    result = Qit().run(v.iterate())
    assert [(0,0), (1, 7), (3, 2)] == result

    result = Qit().run(v.generate().take(100))
    assert all(i in ((0,0), (1, 7), (3, 2)) for i in result)

def test_sequence_values():
    s1 = [(1,2), (3,4), (7,7)]
    s2 = [(1,1), (2, 2)]
    s3 = []
    s4 = [(4,4), (4,4), (4,4)]

    p = Range(4) * Range(10)
    s = Sequence(p)
    v = s.values(s1, s2, s3, s4)

    result = Qit().run(v.iterate())
    assert result == [ s1, s2, s3, s4 ]

    result = Qit().run(v.generate().take(150))
    assert all(i in [ s1, s2, s3, s4 ] for i in result)
