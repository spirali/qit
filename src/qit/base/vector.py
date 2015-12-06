from qit.base.type import Type
from qit.base.int import Int

class Vector(Type):

    def __init__(self, element_type):
        super().__init__()
        self.element_type = element_type

    @property
    def childs(self):
        return super().childs + (self.element_type,)

    def build(self, builder):
        return "std::vector<{} >".format(
            self.element_type.build(builder))

    def read(self, f):
        size = Int().read(f)
        if size is None:
            return None
        return [ self.element_type.read(f) for i in range(size) ]

    @property
    def write_function(self):
        f = self.prepare_write_function()
        f.code("""
        {{write_int}}(output, value.size());
        for (auto item : value) {
            {{write_function}}(output, item);
        }
        """, write_int=Int().write_function,
             write_function=self.element_type.write_function)
        return f

    def build_constant(self, builder, value):
        return builder.build_vector_constant(self, value)

    def is_python_instance(self, obj):
        return isinstance(obj, tuple) or isinstance(obj, list)

    def transform_python_instance(self, obj):
        return tuple(self.element_type.value(v) for v in obj)
