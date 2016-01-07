from testutils import Qit, init
init()

from qit import Int, Struct, Queue, Variable

def test_queue_variable():
    ctx = Qit()
    s = Struct(Int(), Int())
    q = Queue(s)
    x = Variable(q, "x")
    result = ctx.run(x, args={x: [(11,12), (5, 2)] })
    assert result == [(11, 12), (5, 2)]

def test_vector_constructor():
    ctx = Qit()
    s = Struct(Int(), Int())
    q = Queue(s)
    x = Variable(s, "x")
    result = ctx.run(q.value([x, s.value((7, 2)), (1, 2)]),
            args={x: (11,12)})
    assert result == [ (11, 12), (7, 2), (1, 2) ]
