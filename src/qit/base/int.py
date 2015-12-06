
from qit.base.type import Type
import struct

class Int(Type):

    pass_by_value = True

    struct = struct.Struct('<i')
    struct_size = struct.size

    def build(self, builder):
        return "qint"

    def build_value(self, builder, value):
        assert isinstance(value, int)
        return str(value)

    def read(self, f):
        data = f.read(self.struct_size)
        if not data:
            return None
        return self.struct.unpack(data)[0]

    @property
    def write_function(self):
        f = self.prepare_write_function()
        f.code("fwrite(&value, sizeof(value), 1, output);")
        return f

    def is_python_instance(self, obj):
        return isinstance(obj, int)

    def __repr__(self):
        return "Int()"
