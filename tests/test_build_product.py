from testutils import Qit, init
init()

from qit import Range, Product, Variable, Int
import itertools

def test_product_iterate():
    p = Product((Range(3), "x"), (Range(3), "y"))
    r = list(range(3))
    pairs = set(itertools.product(r, r))
    c = Qit()
    result = c.run(p.iterate())
    assert len(result) == len(pairs)
    assert set(result) == pairs

def test_product_in_product():
    p = Product((Range(2), "x"), (Range(2), "y"))
    q = Product((p, "p1"), (p, "p2"))

    r = list(range(2))
    p_all = list(itertools.product(r, r))
    q_all = set(itertools.product(p_all, p_all))

    c = Qit()
    result = c.run(q.iterate())
    assert set(result) == q_all
    assert len(result) == len(q_all)

def test_random_product():
    p = Product((Range(2), "x"), (Range(2), "y"))
    q = Product((p, "p1"), (p, "p2"))
    c = Qit()
    result = c.run(q.generate().take(100))
    assert len(result) == 100
    for ((a, b), (c, d)) in result:
        assert a >= 0 and a < 2
        assert b >= 0 and b < 2
        assert c >= 0 and c < 2
        assert d >= 0 and d < 2

def test_product_no_name():
    p = Product(Range(2), Range(3))
    result = Qit().run(p.iterate())
    assert set(itertools.product(range(2), range(3))) == set(result)

def test_product_copy():
    p = Product((Range(4), "x"), (Range(4), "y"))

    p2 = p.copy()
    p2.set("x", Range(2))

    q = Product((p, "p1"), (p, "p2"))

    q2 = q.copy()
    q2.set_generator("p2", p2.generator)
    q2.set_iterator("p1", p2.iterator)

    v_r4 = list(range(4))
    v_r2 = list(range(2))
    v_p = list(itertools.product(v_r4, v_r4))
    v_p2 = list(itertools.product(v_r2, v_r4))
    v_q2_generator = set(itertools.product(v_p, v_p2))
    v_q2_iterator = set(itertools.product(v_p2, v_p))

    c = Qit()
    for v in c.run(q2.generate().take(200)):
        assert v in v_q2_generator

    result = c.run(q2.iterate())
    assert len(v_q2_iterator) == len(result)
    assert v_q2_iterator == set(result)

def test_product_big():
    R2 = Range(2)
    R3 = Range(3)
    P = R3 * R2 * R3 * R3 * R2 * R2 * R3

    r2 = list(range(2))
    r3 = list(range(3))
    p = set(itertools.product(r3, r2, r3, r3, r2, r2, r3))

    result = Qit().run(P.iterate())
    assert len(result) == len(p)
    assert set(result) == p

    result = Qit().run(P.generate().take(1000))
    for v in result:
        assert v in p

def test_product_construct_names():

    r1 = Range(10)
    r2 = Range(20)

    p1 = Product((r1, "x"), (r2, "y"))
    p2 = Product((r1, "x"), (r2, "y"))
    p3 = Product((r1, "x"), (r1, "y"))

    assert p1 == p2
    assert p1 != p3
    assert p2 != p3

def test_product_construct_noname():

    r1 = Range(10)
    r2 = Range(20)

    p1 = Product(r1, r2)
    p2 = r1 * r2

    assert p1 == p2

    p3 = Product(r1, r2, r1)
    p4 = r1 * r2 * r1

    assert p1 != p3
    assert p1 != p4
    assert p3 == p4

def test_product_variables():
    x = Variable(Int(), "x")
    y = Variable(Int(), "x")

    t = Range(x) * Range(y)
    assert set() == set(t.get_variables())
    assert {x, y} == set(t.iterate().get_variables())
    assert {x, y} == set(t.generate().get_variables())

def test_product_generator_iterator_variables():
    x = Variable(Int(), "x")
    y = Variable(Int(), "x")
    z = Variable(Int(), "z")

    p = Product((Range(z), "a"), (Range(z), "b"))
    p.set_iterator("a", Range(x).iterator)
    p.set_generator("b", Range(y).generator)

    assert set() == set(p.get_variables())
    assert {z, x} == set(p.iterate().get_variables())
    assert {z, y} == set(p.generate().get_variables())

    p.set_iterator("b", Range(12).iterator)
    p.set_generator("a", Range(12).generator)

    assert set() == set(p.get_variables())
    assert {x} == set(p.iterate().get_variables())
    assert {y} == set(p.generate().get_variables())
