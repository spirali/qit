from testutils import Qit, init
init()

from qit import Range, Product, Variable, Int, Sequence, Struct, Function, Functor, FunctorFromFunction, Vector

def test_function_in_function():
    c = Qit()
    x = Variable(Int(), "x")
    r = Range(x).iterate()
    f = r.make_function()

    r2 = Range(x).iterate().map(f)
    f = r2.make_function((x,))

    r3 = Range(x).iterate().map(f)
    assert [[], [[]], [[], [0]], [[], [0], [0,1]]] == c.run(r3, args={ x: 4 })

def test_outer_variables():
    c = Qit()
    x = Variable(Int(), "x")
    f = Function().takes(Int(), "a").returns(Int()).reads(x)
    f.code("return a * x;")
    r = Range(x).iterate().map(f)
    assert [0, 5, 10, 15, 20] == c.run(r, args={ x: 5 })


def test_outer_variables_in_fn_iterator():
    c = Qit()
    x = Variable(Int(), "x")
    y = Variable(Int(), "y")

    plus_1 = Function().takes(Int(), "x").returns(Int()).code("return x + 1;")
    P = Range(plus_1(x)) * Range(y)
    f = P.iterate().to_vector().make_function((x,))

    result = c.run(Range(3).iterate().map(f), args={ y: 2})
    assert [[(0, 0), (0, 1)],
            [(0, 0), (1, 0), (0, 1), (1, 1)],
            [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)]] == result

def test_apply_function_nofree_vars():
    c = Qit()
    x = Variable(Int(), "x")
    y = Variable(Int(), "y")
    f = Function().takes(Int(), "a").returns(Int()).reads(y).code("return a + y;")
    assert [0,1,2,3,4] == c.run(Range(f(x)).iterate(), args={x: 3, y: 2})

def test_apply_function_free_vars():
    c = Qit()
    x = Variable(Int(), "x")
    f = Function().takes(Int(), "a").returns(Int()).code("return a + 10;")
    assert list(range(13)) == c.run(Range(f(x)).iterate(), args={x: 3})

def test_apply_function_constant():
    c = Qit()
    f = Function().takes(Int(), "a").returns(Int()).code("return a + 10;")
    assert list(range(16)) == c.run(Range(f(6)).iterate())

def test_function_constant():
    c = Qit()
    f = Int().value(7).make_function()
    result = c.run(f())
    assert result == 7

def test_function_transport_freevars():
    ctx = Qit()
    x = Int().variable("x")
    f = Function().returns(Int()).code("return {{x}};", x=x)
    g = Function().returns(Int()).code("return {{f}}();", f=f)
    assert 11 == ctx.run(g(), args={x: 11 })

def test_basic_functor():
    ctx = Qit()

    f_functor = Functor("f_functor", Int(), (Int(), "x"), (Int(), "y"))
    f = Function("f").takes(Int(), "x").takes(Int(), "y").returns(Int()).code("return x + y;")
    g = Function("g").takes(f_functor, "f")\
                     .takes(Int(), "x")\
                     .takes(Int(), "y")\
                     .returns(Int())
    g.code("return f(x, y);")
    assert ctx.run(g(f_functor.value(f), 3, 4)) == 7

    f_functor = FunctorFromFunction(f)
    assert ctx.run(g(f_functor.value(f), -2, 4)) == 2

def test_functor_as_function_paramter():
    ctx = Qit()
    s = Struct((Int(), "x"), (Int(), "y"))
    f = Function("f").takes(s, "s").returns(Int()).code("return s.x;")
    ftype = FunctorFromFunction(f)
    g = Function("g").takes(Int(), "x")\
                     .takes(Int(), "y")\
                     .takes(ftype, "f")\
                     .returns(Int())
    g.code("""
        {{stype}} s(x, y);
        return y * f(s);
    """, stype=s)

    assert ctx.run(g(3, 2, ftype.value(f))) == 6

def test_returning_functor():
    c = Qit()

    ftype = Functor("f", Int(), (Int(), "x"))
    g = Function().takes(ftype, "f").takes(Int(), "x").returns(ftype.return_type).code(" return f(x); ")

    h = Function().returns(ftype).code("""
        return [] ({{ptype}} x) { return x - 1; };
    """, ptype=Int())

    assert c.run(g(h(), 3)) == 2

def test_functor_variable():
    ctx = Qit()
    ftype = Functor("f_functor", Int(), (Int(), "x"), (Int(), "y"))

    # functions
    fplus = Function().takes(Int(), "x").takes(Int(), "y").returns(Int())
    fplus.code("return x + y;")

    ftimes = Function().takes(Int(), "x").takes(Int(), "y").returns(Int())
    ftimes.code("return x * y;")

    fmod = Function().takes(Int(), "x").takes(Int(), "y").returns(Int())
    fmod.code("return x % y;")

    # apply function in variable fvar to the given list of pairs
    fvar = ftype.variable("f")
    p = Product((Range(1, 4), "x"), (Range(1, 3), "y"))
    apply_f = Function().takes(p, "p").reads(fvar).returns(Int()).code("""
        return f(p.x, p.y);
    """)
    g = p.iterate().map(apply_f).make_function((fvar, ))

    bind_function = Function().takes(ftype, "f")\
                              .returns(Vector(ftype.return_type))
    bind_function.code("return {{g}}(f);", g=g)
    res = ctx.run(ftype.values(fplus, ftimes, fmod).iterate().map(bind_function))
    assert res == [[2, 3, 4, 3, 4, 5], [1, 2, 3, 2, 4, 6], [0, 0, 0, 1, 0, 1]]
