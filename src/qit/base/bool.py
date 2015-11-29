
from qit.base.type import Type
import struct

class Bool(Type):

    struct = struct.Struct('<?')
    struct_size = struct.size

    def build_type(self, builder):
        return builder.build_bool_type()

    def build_constant(self, builder, value):
        return builder.build_bool_constant(value)

    def is_python_instance(self, obj):
        return isinstance(obj, bool)

    def read(self, f):
        data = f.read(self.struct_size)
        if not data:
            return None
        return self.struct.unpack(data)[0]


