from testutils import Qit, init
init()

from qit import Range, Variable, Int, Function

def test_range_iterate():
    expr = Range(10).iterate()
    c = Qit()
    assert list(range(10)) == c.run(expr)

def test_range_generate():
    expr = Range(10).generate().take(10)
    c = Qit()
    lst = c.run(expr)
    assert len(lst) == 10
    assert all(i >= 0 and i < 10 for i in lst)

def test_range_variable_iterate():
    c = Qit()
    x = Variable(Int(), "x")
    r = Range(x).iterate()
    assert list(range(10)) == c.run(r, { "x": 10 })

def test_range_variable_generate():
    c = Qit()
    x = Variable(Int(), "x")
    r = Range(x).generate().take(30)
    result = c.run(r, { "x": 3 })
    for i in result:
        assert 0 <= i < 3

def test_range_function_iterate():
    c = Qit()

    x = Variable(Int(), "x")
    r = Range(x).iterate().to_vector()
    f = r.make_function()
    assert [[], [0], [0,1], [0,1,2]] == c.run(Range(4).iterate().map(f))

def test_range_function_generate():
    f = Function().takes(Int(), "a").returns(Int()).code("return a + 1;")
    c = Qit()

    x = Variable(Int(), "x")
    r = Range(f(x)).generate().take(2).to_vector()
    f = r.make_function()
    result = c.run(Range(10).iterate().map(f))

    assert len(result) == 10
    for i, r in enumerate(result):
        assert len(r) == 2
        assert 0 <= r[0] < i+1

def test_min_range_iterate():
    expr = Range(15, 42).iterate()
    c = Qit()
    assert list(range(15, 42)) == c.run(expr)

def test_min_range_generate():
    expr = Range(15, 42).generate().take(100)
    c = Qit()
    lst = c.run(expr)
    assert len(lst) == 100
    assert all(i >= 15 and i < 42 for i in lst)

def test_min_step_range_iterate():
    expr = Range(9, 18, 2).iterate()
    c = Qit()
    assert list(range(9, 18, 2)) == c.run(expr)

def test_min_step_range_iterate_variables():
    x = Variable(Int(), "x")
    y = Variable(Int(), "y")
    z = Variable(Int(), "z")
    expr = Range(x, y, z).iterate()
    c = Qit()
    assert list(range(10, 20, 4)) == c.run(expr, args={"x": 10, "y": 20, "z": 4})

def test_range_size():
    ctx = Qit()
    r = Range(11)
    assert ctx.run(r.size) == 11

    start = Variable(Int(), "start")
    end = Variable(Int(), "end")
    step = Variable(Int(), "step")
    r = Range(start, end, step)
    assert ctx.run(r.size, args={ "start" : 5, "end" : 10, "step" : 1 }) == 5
    assert ctx.run(r.size, args={ "start" : 5, "end" : 10, "step" : 2 }) == 2

def test_range_indexer():
    ctx = Qit()
    r = Range(10)
    ctx.run(r.indexer(5)) == 5

    start = Variable(Int(), "start")
    end = Variable(Int(), "end")
    step = Variable(Int(), "step")
    r = Range(start, end, step)
    result = ctx.run(r.iterate().map(r.indexer), args={"start" : 5, "end": 21, "step" : 3})
    assert result == list(range(6))
