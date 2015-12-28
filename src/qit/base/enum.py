
from qit.base.type import Type
from qit.base.utils import is_valid_name
import struct

class Enum(Type):

    pass_by_value = True

    struct = struct.Struct('@i')
    struct_size = struct.size

    def __init__(self, *names):
        self.names = tuple(names)
        assert all(is_valid_name(name) for name in self.names)

    def build_value(self, builder, value):
        assert isinstance(value, str)
        return str(value)

    def read(self, f):
        data = f.read(self.struct_size)
        if not data:
            return None
        return self.names[self.struct.unpack(data)[0]]

    def read_index(self, f):
        data = f.read(self.struct_size)
        if not data:
            return None
        return self.struct.unpack(data)[0]

    def first(self):
        return self.value(self.names[0])

    @property
    def write_function(self):
        f = self.prepare_write_function()
        f.code("fwrite(&value, sizeof(value), 1, output);")
        return f

    def is_python_instance(self, obj):
        return isinstance(obj, str)

    def declare(self, builder):
        if builder.check_declaration_key(self):
            return
        builder.writer.line("enum {} : int {{ {} }};",
                            self.build(builder),
                            ",".join(self.names))

    def __repr__(self):
        return "Enum({})".format(",".join(self.names))
