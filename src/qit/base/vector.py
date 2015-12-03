from qit.base.type import Type
import struct


class Vector(Type):

    struct = struct.Struct('<Q')
    struct_size = struct.size

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
        data = f.read(self.struct_size)
        if not data:
            return None
        size = self.struct.unpack(data)[0]
        return [ self.element_type.read(f) for i in range(size) ]

    def build_constant(self, builder, value):
        return builder.build_vector_constant(self, value)

    def is_python_instance(self, obj):
        return isinstance(obj, tuple) or isinstance(obj, list)

    def transform_python_instance(self, obj):
        return tuple(obj)
