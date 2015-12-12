
from qit.base.type import Type
import struct

class qdict(dict): # NOTICE: standard dictionary is not hasbale?

    def __hash__(self):
        return hash(frozenset(self.items()))

class Map(Type):

    pass_by_value = False

    struct = struct.Struct('<Q')
    struct_size = struct.size

    def __init__(self, domain_type, image_type):
        self.name = None

        self.domain_type = domain_type
        self.image_type = image_type

    def build(self, builder):
        return "std::map<{}, {} >".format(self.domain_type.build(builder),
                                          self.image_type.build(builder))

    def read(self, f):
        data = f.read(self.struct_size)
        if not data:
            return None
        size = self.struct.unpack(data)[0]
        return dict((self.domain_type.read(f), self.image_type.read(f))
                 for i in range(size))

    @property
    def write_function(self):
        functions = (self.domain_type.write_function,
                     self.image_type.write_function)

        f = self.prepare_write_function();
        f.code("""
        size_t size = value.size();
        fwrite(&size, sizeof(size_t), 1, output);
        for (auto it = value.cbegin(); it != value.cend(); ++it) {
            {{ b(_functions[0]) }}(output, it->first);
            {{ b(_functions[1]) }}(output, it->second);
        }
        """, _functions=functions)
        f.uses(functions)
        return f

    def is_python_instance(self, obj):
        return isinstance(obj, dict)

    def value(self, value):
        return super().value(qdict(value))

    def build_value(self, builder, value):
        dom_type = self.domain_type
        img_type = self.image_type
        arg = ",".join("{{ {0}, {1} }}".format(
            dom_type.value(k).build(builder), img_type.value(v).build(builder))
                for k, v in value.items())

        return "{0} ({{ {1} }})".format(self.build(builder), arg)

    def __repr__(self):
        return "Map({}, {})".format(repr(self.domain_type),
                                    repr(self.image_type))
