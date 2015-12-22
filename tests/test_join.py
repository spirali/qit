from testutils import Qit, init
init()

import itertools
from qit import Int, Range, Sequence, Vector, Join


def test_join_range_iterate():
    ctx = Qit()
    d1 = Range(3)
    d2 = Range(0, 0)
    d3 = Range(0, 0)
    d4 = Range(5)

    expected = list(range(3)) + list(range(5))
    j = d1 + d2 + d3 + d4
    result = ctx.run(j.iterate())
    assert expected == result

def test_join_empty_iterate():
    ctx = Qit()
    d1 = Range(0, 0)
    d2 = Range(0, 0)
    j = d1 + d2

    result = ctx.run(j.iterate())
    assert [] == result

    result = ctx.run(j.size)
    assert result == 0

def test_join_sequence_iterate():
    a = [0, 1]
    expected = [ [0], [1], [2], [2, 3], [4, 5] ]
    expected += list(itertools.product(a, a))
    expected += list(itertools.product(a, a, a))
    expected = list(map(list, expected))

    ctx = Qit()
    r1 = Range(3)
    r2 = Range(2)

    d1 = Sequence(r1, 1)
    d2 = Vector(Int()).values([2, 3], [4, 5])
    d3 = Sequence(r2, 2)
    d4 = Sequence(r2, 3)

    j = d1 + d2 + d3 + d4

    result = ctx.run(j.iterate())
    assert sorted(result) == sorted(expected)

    result = ctx.run(j.size)
    assert len(expected) == result


def test_join_int_generate():
    ctx = Qit()

    r1 = Range(2)
    r2 = Range(2, 4)
    j = r1 + r2

    result = ctx.run(j.generate().take(1000))
    assert set(result) == set(range(4))


def test_join_int_generate2():
    ctx = Qit()

    r1 = Int().values(5000)
    r2 = Range(1000)
    r3 = Int().values(5001, 5002)

    j = r1 + r2 + r3

    result = ctx.run(j.generate().take(3000))
    print(result)
    assert result.count(5000) < 100
    assert result.count(5001) < 100
    assert result.count(5002) < 100

def test_join_int_generate3():
    ctx = Qit()

    r1 = Range(2)
    r2 = Range(2, 4)
    r3 = Range(4, 6)

    j = Join((r1, r2, r3), ratios=(1, 0, 1))

    result = ctx.run(j.generate().take(1000))
    assert set(result) == set((0, 1, 4, 5))
