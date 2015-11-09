import testutils

from qit import Range, Product
import qit

def Qit():
    return qit.Qit(debug=True)

def test_range_print_all():
    expr = Range(10)
    c = Qit()
    c.print_all(expr)

def test_range_random_print_all():
    expr = Range(10).random().take(10)
    c = Qit()
    c.print_all(expr)

def test_take_too_much():
    expr = Range(10).take(20)
    c = Qit()
    c.print_all(expr)

def test_product():
    p = Product("MyProduct")
    p.add("x", Range(3))
    p.add("y", Range(3))
    c = Qit()
    c.print_all(p)

def test_product_in_product():
    p = Product("P")
    p.add("x", Range(2))
    p.add("y", Range(2))

    q = Product("Q")
    q.add("p1", p)
    q.add("p2", p)
    c = Qit()
    c.print_all(q)


def test_random_product():
    p = Product("P")
    p.add("x", Range(2))
    p.add("y", Range(2))

    q = Product("Q")
    q.add("p1", p)
    q.add("p2", p)
    c = Qit()
    c.print_all(q.random().take(3))


