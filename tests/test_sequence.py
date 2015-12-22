from testutils import Qit, init
init()

from qit import Range, Sequence, Int, Variable, Domain
import itertools

def test_sequence_collect():

    r = Range(3)
    s = Sequence(r * r, 3)

    rr = range(3)
    pp = list(itertools.product(rr, rr))
    ss = set(itertools.product(pp, pp, pp))

    ctx = Qit()
    result = ctx.run(s.iterate())
    assert len(ss) == len(result)
    assert ss == set(map(tuple, result))

    result = ctx.run(s.generate().take(1000))
    for item in result:
        assert tuple(item) in ss

def test_sequence_of_sequence():
    s = Sequence(Range(3), 5)
    s2 = Sequence(s, 2)

    rr = range(3)
    ss = list(itertools.product(rr, rr, rr, rr, rr))
    ss2 = set(itertools.product(ss, ss))

    result = Qit().run(s2.iterate())
    result = [ map(tuple, i) for i in result ]
    assert len(ss2) == len(result)
    assert ss2 == set(map(tuple, result))

def test_sequence_empty():
    s = Sequence(Range(3), 0)
    assert Qit().run(s.iterate()) == [[]]
    assert Qit().run(s.generate().take(3)) == [[]] * 3

def test_sequence_empty_empty_domain():
    s = Sequence(Range(10, 10), 2)
    assert Qit().run(s.iterate()) == []

def test_sequence_variable():
    ctx = Qit()
    x = Variable(Int(), "x")
    y = Variable(Int(), "y")
    r = Sequence(Range(y), x).iterate()
    result = ctx.run(r, args={x: 2, y : 3})

    rr = list(range(3))
    expected = set(itertools.product(rr, rr))
    assert set(map(tuple, result)) == expected
    assert len(result) == len(expected)

def test_sequence_size():
    ctx = Qit()
    p = Range(2) * Range(5)
    s = Sequence(p, 4)
    assert ctx.run(s.size) == 10000

def test_sequence_size_null():
    d = Domain(Int())
    s = Sequence(d, 4)
    assert s.size is None
