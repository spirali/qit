
from qit.base.type import Type
import struct

class Bool(Type):

    struct = struct.Struct('<?')
    struct_size = struct.size

    def get_element_type(self, builder):
        return builder.get_bool_type()

    def read(self, f):
        data = f.read(self.struct_size)
        if not data:
            return None
        return self.struct.unpack(data)[0]

    def make_instance(self, builder, value):
        return builder.make_bool_instance(value)

    @property
    def basic_type(self):
        return Bool()

    @property
    def iterator(self):
        raise NotImplemented()

    @property
    def generator(self):
        raise NotImplemented()
