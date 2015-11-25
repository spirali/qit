
from qit import Range, Product, Int, Variable

def test_product_construct_named():

    r1 = Range(10)
    r2 = Range(20)

    p1 = Product("p", (r1, "x"), (r2, "y"))
    p2 = Product("p", (r1, "x"), (r2, "y"))
    p3 = Product("p", (r1, "x"), (r1, "y"))

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
