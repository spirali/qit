from testutils import Qit, init
init()

from qit import Range

def test_range_print_all():
    expr = Range(10).iterate()
    c = Qit()
    c.run(expr.print_all())
    assert list(range(10)) == c.run(expr.collect())

def test_range_random_print_all():
    expr = Range(10).generate().take(10).collect()
    c = Qit()
    lst = c.run(expr)
    assert len(lst) == 10
    assert all(i >= 0 and i < 10 for i in lst)
