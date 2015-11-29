
from qit.base.type import Type
import struct

class Int(Type):

    struct = struct.Struct('<i')
    struct_size = struct.size

    def build_type(self, builder):
        return builder.build_int_type()

    def build_constant(self, builder, value):
        return builder.build_int_constant(value)

    def read(self, f):
        data = f.read(self.struct_size)
        if not data:
            return None
        return self.struct.unpack(data)[0]

    def is_python_instance(self, obj):
        return isinstance(obj, int)
