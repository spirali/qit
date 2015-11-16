
from qit.base.type import Type
import struct

class Int(Type):

    struct = struct.Struct('i')
    size = struct.size

    def get_element_type(self, builder):
        return builder.get_int_type()

    def read(self, f):
        data = f.read(self.size)
        if not data:
            return None
        return self.struct.unpack(data)[0]

    @property
    def iterator(self):
        raise NotImplemented()

    @property
    def generator(self):
        raise NotImplemented()
