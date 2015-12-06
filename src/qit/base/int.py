
from qit.base.type import Type
import struct

class Int(Type):

    pass_by_value = True

    struct = struct.Struct('<i')
    struct_size = struct.size

    def build(self, builder):
        return "int"

    def build_constant(self, builder, value):
        assert isinstance(value, int)
        return str(value)

    def read(self, f):
        data = f.read(self.struct_size)
        if not data:
            return None
        return self.struct.unpack(data)[0]

    def is_python_instance(self, obj):
        return isinstance(obj, int)

    def __repr__(self):
        return "Int()"
