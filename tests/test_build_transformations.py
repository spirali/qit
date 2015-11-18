from testutils import Qit, init
init()

from qit import Range, Product, Function

def test_take_too_much():
    expr = Range(10).iterate().take(20)
    c = Qit()
    assert list(range(10)) == c.run(expr)

def test_map():
    p = Product("P", (Range(4), "x"), (Range(4), "y"))
    f = Function("f").takes(p, "p").returns(Range(8)).code("return p.x + p.y;")
    result = Qit().run(p.iterate().take(6).map(f).take(4))
    assert result == [0, 1, 2, 3]
    result = Qit().run(p.generate().map(f).take(4))
    assert all(x >= 0 and x <= 8 for x in result)
