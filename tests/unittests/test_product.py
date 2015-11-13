
from qit import Range, Product

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

    p1 = Product(None, r1, r2)
    p2 = r1 * r2

    assert p1 == p2

    p3 = Product(None, r1, r2, r1)
    p4 = r1 * r2 * r1

    assert p1 != p3
    assert p1 != p4
    assert p3 == p4
