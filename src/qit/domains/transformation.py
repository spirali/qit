
from qit.base.int import Int
from qit.base.struct import Struct
from qit.base.variable import Variable
from qit.base.function import Function
from qit.domains.iterator import Iterator


class Transformation(Iterator):
    pass


class TakeTransformation(Transformation):

    def __init__(self, iterator, count):
        count = Int().value(count)
        itype = Struct(Int(), iterator.itype)
        init_expr = itype.value((count, iterator.init_expr))
        super().__init__(itype, iterator.element_type, init_expr)

        self.next_fn.code("""
            if (iter.v0 <= 1) {
                iter.v0 = 0;
                return;
            }
            iter.v0--;
            {{next_fn}}(iter.v1);
        """, next_fn=iterator.next_fn, itype=itype)

        self.is_valid_fn.code("""
            if (iter.v0 <= 0) {
                return false;
            } else {
                return {{is_valid_fn}}(iter.v1);
            }
        """, is_valid_fn=iterator.is_valid_fn)

        self.value_fn.code("return {{value_fn}}(iter.v1);",
                value_fn=iterator.value_fn)


class MapTransformation(Transformation):

    def __init__(self, iterator, function):
        super().__init__(iterator.itype,
                         function.return_type,
                         iterator.init_expr)
        assert function.return_type is not None
        # TODO: Check compatibility of function and valid return type
        self.next_fn = iterator.next_fn
        self.is_valid_fn = iterator.is_valid_fn
        x = Variable(iterator.itype, "_x")
        self.value_fn = function(iterator.value_fn(x)).make_function((x,))


class SortTransformation(Transformation):

    def __init__(self, iterator, ascending=True):
        raise Exception("TODO")

class FilterTransformation(Transformation):

    def __init__(self, iterator, function):
        itype = iterator.itype
        init_expr = Function().returns(itype).code("""
            {{itype}} result = {{init_expr}};
            for(;;) {
                if (!{{is_valid_fn}}(result)) {
                    return result; // Iterator is empty
                }
                if ({{function}}({{value_fn}}(result))) {
                    return result; // We have found a value
                }
                {{next_fn}}(result);
            }
            """,
            init_expr=iterator.init_expr,
            itype=iterator.itype,
            next_fn=iterator.next_fn,
            is_valid_fn=iterator.is_valid_fn,
            value_fn=iterator.value_fn,
            function=function)()
        super().__init__(iterator.itype,
                         iterator.element_type,
                         init_expr)
        self.is_valid_fn = iterator.is_valid_fn
        self.value_fn = iterator.value_fn
        self.next_fn.code("""
            {{next_fn}}(iter);
            for(;;) {
                if (!{{is_valid_fn}}(iter)) {
                    return; // Iterator is empty
                }
                if ({{function}}({{value_fn}}(iter))) {
                    return; // We have found a value
                }
                {{next_fn}}(iter);
            }
            """,
            next_fn=iterator.next_fn,
            is_valid_fn=iterator.is_valid_fn,
            value_fn=iterator.value_fn,
            function=function)

