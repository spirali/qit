
from qit.base.function import Function
from qit.base.bool import Bool
from qit.base.vector import Vector
from qit.base.qitobject import QitObject

class IteratorType:
    pass # DELETEME

class Iterator(QitObject):

    def __init__(self, itype, element_type, init_expr):
        self.itype = itype
        self.element_type = element_type
        self.init_expr = init_expr
        self.next_fn = Function().takes(itype, "iter").returns(itype)
        self.is_valid_fn = Function().takes(itype, "iter").returns(Bool())
        self.value_fn = Function().takes(itype, "iter").returns(element_type)

    @property
    def childs(self):
        return (self.itype,
                self.init_expr,
                self.next_fn,
                self.is_valid_fn,
                self.value_fn)

    # Transformations

    def take(self, count):
        return TakeTransformation(self, count)

    def map(self, function):
        return MapTransformation(self, function)

    def sort(self, asceding=True):
        return SortTransformation(self, asceding)

    def filter(self, function):
        return FilterTransformation(self, function)

    def to_vector(self):
        vector = Vector(self.element_type)
        f = Function(returns=vector)
        f.code(
            """
                {{vector}} output;
                {{itype}} iterator = {{init_expr}};
                while({{is_valid_fn}}(iterator)) {
                    output.push_back({{value_fn}}(iterator));
                    iterator = {{next_fn}}(iterator);
                };
                return output;
            """,
            itype=self.itype,
            init_expr=self.init_expr,
            next_fn=self.next_fn,
            is_valid_fn=self.is_valid_fn,
            value_fn=self.value_fn,
            vector=vector)
        return f()

    def make_function(self, *args, **kw):
        return self.get_expression().make_function(*args, **kw)

    def get_expression(self):
        return self.to_vector()


class VectorIterator(Iterator):

    def __init__(self, expression):
        vector = expression.type


# To broke import cycle, we import following packages at the end
from qit.base.transformation import TakeTransformation, FilterTransformation
from qit.base.transformation import MapTransformation
from qit.base.transformation import SortTransformation
