from testutils import Qit, init
init()

from qit import Range, Product, Function, Sequence, Variable, Int

def test_take_too_much():
    expr = Range(10).iterate().take(20)
    c = Qit()
    assert list(range(10)) == c.run(expr)

def test_take_variable():
    ctx = Qit()
    x = Variable(Int(), "x")
    r = Range(10).generate().take(x)
    result = ctx.run(r, args={x: 5})
    assert len(result) == 5

def test_map():
    p = Product((Range(4), "x"), (Range(4), "y"))
    f = Function("f").takes(p.type, "p").returns(Int()).code("return p.x + p.y;")
    result = Qit().run(p.iterate().take(6).map(f).take(4))
    assert result == [0, 1, 2, 3]

    result = Qit().run(p.iterate().take(6).map_kv(f).take(4))
    assert result == [((0,0), 0), ((1, 0), 1), ((2, 0), 2), ((3, 0), 3)]

    result = Qit().run(p.generate().map(f).take(4))
    assert all(x >= 0 and x <= 8 for x in result)

def test_sort():
    def check(results):
        for i, a in enumerate(results[:-1]):
            assert a <= results[i+1]
    #print(Qit().run((Sequence(Range(10), 3) * Range(3)).generate().take(100)))
    results = Qit().run((Sequence(Range(10), 3) * Range(3)).generate().take(1))
    check(results)
    results = Qit().run(Range(5).generate().take(1000).sort())
    check(results)
