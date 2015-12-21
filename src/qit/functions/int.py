from qit.base.function import Function
from qit.base.int import Int

def multiplication_n(size):
     f = Function().returns(Int())
     for i in range(size):
        f.takes(Int())
     code = "*".join(p.name for p in f.params)
     f.code("return {};".format(code))
     return f

mul = multiplication_n(2)

def addition_n(size):
     f = Function().returns(Int())
     for i in range(size):
        f.takes(Int())
     code = "+".join(p.name for p in f.params)
     f.code("return {};".format(code))
     return f

add = addition_n(2)

# Naive way of making power, but it is sufficient for now
power = Function().takes(Int(), "base").takes(Int(), "power").returns(Int())
power.code("""
    int result = 1;
    int p = power;
    while(p > 0) {
        result *= base;
        p--;
    }
    return result;
""")

identity = Function().takes(Int(), "a").returns(Int()).code("return a;")

subtract = Function().takes(Int(), "a").takes(Int(), "b").returns(Int())
subtract.code("return a - b;")
