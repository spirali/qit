
from qit.base.type import Type
import struct

class Bool(Type):

    pass_by_value = True

    struct = struct.Struct('<?')
    struct_size = struct.size

    def build(self, builder):
        return "bool"

    def build_value(self, builder, value):
        assert isinstance(value, bool)
        return "true" if value else "false"

    def is_python_instance(self, obj):
        return isinstance(obj, bool)

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
