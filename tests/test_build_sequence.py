from testutils import Qit, init
init()

from qit import Range, Sequence
import itertools

def test_sequence_collect():

    r = Range(3)
    s = Sequence(r * r, 3)

    rr = range(3)
    pp = list(itertools.product(rr, rr))
    ss = set(itertools.product(pp, pp, pp))

    result = Qit().run(s.iterate().collect())
    assert len(ss) == len(result)
    assert ss == set(map(tuple, result))

    result = Qit().run(s.generate().take(1000).collect())
    for item in result:
        assert tuple(item) in ss

def test_sequence_of_sequence():
    s = Sequence(Range(3), 5)
    s2 = Sequence(s, 2)

    rr = range(3)
    ss = list(itertools.product(rr, rr, rr, rr, rr))
    ss2 = set(itertools.product(ss, ss))

    result = Qit().run(s2.iterate().collect())
    result = [ map(tuple, i) for i in result ]
    assert len(ss2) == len(result)
    assert ss2 == set(map(tuple, result))


def test_empty_sequence():
    s = Sequence(Range(3), 0)
    assert Qit().run(s.iterate().collect()) == [[]]
    assert Qit().run(s.generate().take(3).collect()) == [[]] * 3
