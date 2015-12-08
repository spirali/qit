from testutils import Qit, init
init()

from qit import Enumerate

def test_enumerate_iterate():
    ctx = Qit()
    e = Enumerate("A", "B", "C")
    assert ctx.run(e.iterate()) == ["A", "B", "C"]

def test_enumerate_generate():
    ctx = Qit()
    e = Enumerate("A", "B", "C")
    result = ctx.run(e.generate().take(1000))
    assert set(result) == set(["A", "B", "C"])

def test_enumerate_size():
    ctx = Qit()
    e = Enumerate("A", "B", "C", "D")
    assert ctx.run(e.size) == 4
