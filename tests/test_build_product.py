from testutils import Qit, init
init()

from qit import Range, Product
import itertools

def test_product_iterate():
    p = Product("MyProduct", (Range(3), "x"), (Range(3), "y"))
    r = list(range(3))
    pairs = set(itertools.product(r, r))
    c = Qit()
    result = c.run(p.iterate().collect())
    assert len(result) == len(pairs)
    assert set(result) == pairs

def test_product_in_product():
    p = Product("P", (Range(2), "x"), (Range(2), "y"))
    q = Product("Q", (p, "p1"), (p, "p2"))

    r = list(range(2))
    p_all = list(itertools.product(r, r))
    q_all = set(itertools.product(p_all, p_all))

    c = Qit()
    result = c.run(q.iterate().collect())
    assert set(result) == q_all
    assert len(result) == len(q_all)

def test_random_product():
    p = Product("P", (Range(2), "x"), (Range(2), "y"))
    q = Product("Q", (p, "p1"), (p, "p2"))
    c = Qit()
    result = c.run(q.generate().take(100).collect())
    assert len(result) == 100
    for ((a, b), (c, d)) in result:
        assert a >= 0 and a < 2
        assert b >= 0 and b < 2
        assert c >= 0 and c < 2
        assert d >= 0 and d < 2

def test_product_no_name():
    p = Product(None, Range(2), Range(3))
    Qit().run(p.iterate().print_all())

def test_product_copy():
    p = Product("P", (Range(4), "x"), (Range(4), "y"))

    p2 = p.copy()
    p2.set("x", Range(2))

    q = Product("Q", (p, "p1"), (p, "p2"))

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
    for v in c.run(q2.generate().take(200).collect()):
        assert v in v_q2_generator

    result = c.run(q2.iterate().collect())
    assert len(v_q2_iterator) == len(result)
    assert v_q2_iterator == set(result)

def test_product_big():
    R2 = Range(2)
    R3 = Range(3)
    P = R3 * R2 * R3 * R3 * R2 * R2 * R3

    r2 = list(range(2))
    r3 = list(range(3))
    p = set(itertools.product(r3, r2, r3, r3, r2, r2, r3))

    result = Qit().run(P.iterate().collect())
    assert len(result) == len(p)
    assert set(result) == p

    result = Qit().run(P.generate().take(1000).collect())
    for v in result:
        assert v in p
