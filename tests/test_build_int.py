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
