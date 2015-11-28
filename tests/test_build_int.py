from testutils import Qit, init
init()

from qit import Range

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
