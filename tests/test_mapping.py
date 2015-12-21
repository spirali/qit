from testutils import Qit, init
init()

from qit import Mapping, Range, Enumerate, Sequence, Function, Int

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

def test_mapping2_generator():
    ctx = Qit()
    r1 = Range(10)
    r2 = Range(10, 20)
    r3 = Range(20, 30)

    f = Function().takes(Int(), "a").returns(Int()).code("""
        return (a % 2) + 1;
    """)

    m = Mapping(Range(10), (r1, r2, r3), choose_fn=f)
    result = ctx.run(m.generate().take(500))
    assert len(result) == 500
    for r in result:
        assert sorted(r.keys()) == list(range(10))
        for i in range(0, 10, 2):
            assert r[i] >= 10 and r[i] < 20
        for i in range(1, 10, 2):
            assert r[i] >= 20 and r[i] < 30

def test_mapping2_iterator():
    ctx = Qit()
    r = Range(2)
    v = Int().values(7, 10)
    fn = Function().takes(Int(), "x").returns(Int()).code("return x % 2;")
    m = Mapping(r, (r, v), choose_fn=fn)

    result = ctx.run(m.iterate())
    expected = [ {0: 0, 1: 7},
                 {0: 1, 1: 7},
                 {0: 0, 1: 10},
                 {0: 1, 1: 10}]

    assert set(map(hdict, expected)) == set(map(hdict, result))

def test_mapping_size():
    ctx = Qit()
    x = Int().variable("x")
    m = Mapping(Range(10), Range(x))
    assert ctx.run(m.size, args={ "x": 2}) == 1024

def test_mapping2_size():
    ctx = Qit()
    fn = Function().takes(Int(), "x").returns(Int()).code("return x < 1 ? 2 : 0;")
    m = Mapping(Range(4), (Range(2), Range(10),  Range(4)), choose_fn=fn)
    assert ctx.run(m.size) == 32
