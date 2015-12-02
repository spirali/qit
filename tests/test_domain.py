from testutils import Qit, init
init()

from qit import Int, Domain

def test_domain_constant_generator():
    c = Qit()
    s = Int() * Int()
    f = s.const((7, 8)).make_function()
    d = Domain(Int(), generator=f())

    result = c.run(d.generate().take(5))
    assert result == [ (7, 8) ] * 5
