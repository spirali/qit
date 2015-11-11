import testutils

from qit import Range, Product, Function
import qit

def Qit():
    return qit.Qit(debug=True)

def test_range_print_all():
    expr = Range(10).iterate()
    c = Qit()
    c.print_all(expr)

def test_range_random_print_all():
    expr = Range(10).generate().take(10)
    c = Qit()
    c.print_all(expr)

def test_take_too_much():
    expr = Range(10).iterate().take(20)
    c = Qit()
    c.print_all(expr)

def test_product():
    p = Product("MyProduct")
    p.add("x", Range(3))
    p.add("y", Range(3))
    c = Qit()
    c.print_all(p.iterate())

def test_product_in_product():
    p = Product("P")
    p.add("x", Range(2))
    p.add("y", Range(2))

    q = Product("Q")
    q.add("p1", p)
    q.add("p2", p)
    c = Qit()
    c.print_all(q.iterate())

def test_random_product():
    p = Product("P")
    p.add("x", Range(2))
    p.add("y", Range(2))

    q = Product("Q")
    q.add("p1", p)
    q.add("p2", p)
    c = Qit()
    c.print_all(q.generate().take(3))

def test_map():
    p = Product("P")
    p.add("x", Range(4))
    p.add("y", Range(4))
    f = Function("f").takes(p, "p").returns(Range(4)).code("return p.x + p.y;")
    Qit().print_all(p.iterate().take(6).map(f).take(4))
    Qit().print_all(p.generate().map(f).take(4))

def test_derive():
    p = Product("P")
    p.add("x", Range(10))
    p.add("y", Range(10))

    p2 = p.derive()
    p2.set("x", Range(2))

    q = Product("Q")
    q.add("p1", p)
    q.add("p2", p)

    q2 = q.derive()
    q2.set_generator("p2", p2.generator)
    q2.set_iterator("p1", p2.iterator)

    c = Qit()
    c.print_all(q2.generate().take(10))
    c.print_all(q2.iterate().take(20))
