from testutils import Qit, init
init()

from qit import Mapping, Range, Enumerate, Sequence

class hdict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


def test_mapping_int_int():
    ctx = Qit()
    r = Range(2)
    m = Mapping(r, r)
    result = ctx.run(m.iterate())
    assert set(map(hdict, result)) == \
           set(map(hdict, [{0: 0, 1: 0}, {0: 1, 1: 0},
                           {0: 0, 1: 1}, {0: 1, 1: 1}]))


def test_mapping_product_sequence():
    ctx = Qit()
    r = Range(2) * Range(1)
    s = Sequence(Enumerate("X", "Y"), 2)
    m = Mapping(r, s)
    result = ctx.run(m.iterate())

    expected = [
            {(1, 0): ['X', 'X'], (0, 0): ['X', 'X']},
            {(1, 0): ['X', 'X'], (0, 0): ['Y', 'X']},
            {(1, 0): ['X', 'X'], (0, 0): ['X', 'Y']},
            {(1, 0): ['X', 'X'], (0, 0): ['Y', 'Y']},
            {(1, 0): ['Y', 'X'], (0, 0): ['X', 'X']},
            {(1, 0): ['Y', 'X'], (0, 0): ['Y', 'X']},
            {(1, 0): ['Y', 'X'], (0, 0): ['X', 'Y']},
            {(1, 0): ['Y', 'X'], (0, 0): ['Y', 'Y']},
            {(1, 0): ['X', 'Y'], (0, 0): ['X', 'X']},
            {(1, 0): ['X', 'Y'], (0, 0): ['Y', 'X']},
            {(1, 0): ['X', 'Y'], (0, 0): ['X', 'Y']},
            {(1, 0): ['X', 'Y'], (0, 0): ['Y', 'Y']},
            {(1, 0): ['Y', 'Y'], (0, 0): ['X', 'X']},
            {(1, 0): ['Y', 'Y'], (0, 0): ['Y', 'X']},
            {(1, 0): ['Y', 'Y'], (0, 0): ['X', 'Y']},
            {(1, 0): ['Y', 'Y'], (0, 0): ['Y', 'Y']} ]

    def to_tuple(d):
        for key, value in d.items():
            return (tuple(key), tuple(value))

    assert set(map(to_tuple, result)) == set(map(to_tuple, expected))

def test_mapping_generator():
    ctx = Qit()
    m = Mapping(Range(5, 7), Range(2, 8))
    result = ctx.run(m.generate().take(100))
    assert len(result) == 100
    for r in result:
        assert set(r.keys()) == set((5, 6))
        assert set(r.values()).issubset(set((2, 3, 4, 5, 6, 7)))
