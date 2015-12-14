
from qit.base.int import Int
from qit.base.type import Type

class Map(Type):

    def __init__(self, domain_type, image_type):
        self.name = None

        self.domain_type = domain_type
        self.image_type = image_type

    @property
    def childs(self):
        return (self.domain_type, self.image_type)

    def childs_from_value(self, value):
        return tuple(v[0] for v in value) + tuple(v[1] for v in value)

    def build(self, builder):
        return "std::map<{}, {} >".format(self.domain_type.build(builder),
                                          self.image_type.build(builder))

    def read(self, f):
        size = Int().read(f)
        return dict((self.domain_type.read(f), self.image_type.read(f))
                 for i in range(size))

    @property
    def write_function(self):
        f = self.prepare_write_function();
        f.code("""
        {{write_int}}(output, value.size());
        for (auto it = value.cbegin(); it != value.cend(); ++it) {
            {{ key_write }}(output, it->first);
            {{ value_write }}(output, it->second);
        }
        """, key_write=self.domain_type.write_function,
             value_write=self.image_type.write_function,
             write_int=Int().write_function)
        return f

    def is_python_instance(self, obj):
        return isinstance(obj, dict)

    def transform_python_instance(self, obj):
        return frozenset((self.domain_type.value(k), self.image_type.value(v))
                     for k, v in obj.items())

    def build_value(self, builder, value):
        arg = ",".join("{{ {0}, {1} }}".format(
            value.build(builder), image.build(builder))
                for value, image in value)
        return "{0} ({{ {1} }})".format(self.build(builder), arg)

    def __repr__(self):
        return "Map({}, {})".format(repr(self.domain_type),
                                    repr(self.image_type))
