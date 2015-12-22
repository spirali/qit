from testutils import Qit, init
init()

from qit import Int, Struct, Variable, Class, Function

def test_class_method():
    ctx = Qit()
    p = Struct((Int(), "x"), (Int(), "y"))
    m1 = p.method("get").returns(Int()).code("return self.x + self.y;")
    cls = Class(p, (m1,))
    f = Function().returns(Int()).takes(cls, "a").code("return a.get();")
    result = ctx.run(f(cls.value((20, 31))))
    assert result == 51


def test_class_method_free_var():
    ctx = Qit()
    p = Struct((Int(), "x"), (Int(), "qit_freevar_y"))
    y = Variable(Int(), "y")
    m1 = p.method("get").returns(Int()).reads(y).takes(Int(), "a")
    m1.code("return a + {{y}};", y=y)
    cls = Class(p, (m1,))
    f = Function().returns(Int()).takes(cls, "a").code("return a.get(5);")
    result = ctx.run(f(cls.value((20, 31))))
    assert result == 36
