
from qit.base.int import Int
from qit.base.type import Type
from qit.base.bool import Bool
from qit.base.function import FunctorFromFunction

class Map(Type):

    def __init__(self, key_type, value_type, key_cmp_fn=None):
        self.name = None

        self.key_type = key_type
        self.value_type = value_type
        self.key_cmp_fn = key_cmp_fn
        self.key_cmp_functor = None
        if key_cmp_fn is not None:
            assert (isinstance(key_cmp_fn.return_type, Bool) and
                    len(key_cmp_fn.params) and
                    all(map(lambda p: isinstance(p.type, key_type.__class__),
                            key_cmp_fn.params)))
            self.key_cmp_functor = FunctorFromFunction(key_cmp_fn)

    @property
    def childs(self):
        childs = (self.key_type, self.value_type)
        if self.key_cmp_functor is not None:
            childs += (self.key_cmp_fn, self.key_cmp_functor)
        return childs

    def childs_from_value(self, value):
        return tuple(v[0] for v in value) + tuple(v[1] for v in value)

    def build(self, builder):
        if self.key_cmp_functor is None:
            return "std::map<{}, {} >".format(self.key_type.build(builder),
                                              self.value_type.build(builder))
        return "std::map<{}, {}, {} >".format(self.key_type.build(builder),
                                              self.value_type.build(builder),
                                              self.key_cmp_functor.build(builder))

    def build_destructor(self, builder):
        return "~map<{}, {} >".format(self.key_type.build(builder),
                                      self.value_type.build(builder))

    def read(self, f):
        size = Int().read(f)
        return dict((self.key_type.read(f), self.value_type.read(f))
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
        """, key_write=self.key_type.write_function,
             value_write=self.value_type.write_function,
             write_int=Int().write_function)
        return f

    def is_python_instance(self, obj):
        return isinstance(obj, dict)

    def transform_python_instance(self, obj):
        return frozenset((self.key_type.value(k), self.value_type.value(v))
                     for k, v in obj.items())

    def build_value(self, builder, value):
        arg = ",".join("{{ {0}, {1} }}".format(
            value.build(builder), image.build(builder))
                for value, image in value)
        if self.key_cmp_fn is None:
            return "{0} ({{ {1} }})".format(self.build(builder), arg)
        return "{0} ({{ {1} }}, {2})".format(self.build(builder), arg,
                builder.get_name(self.key_cmp_fn))

    def __repr__(self):
        if self.key_cmp_functor is None:
            return "Map({}, {})".format(repr(self.key_type),
                                        repr(self.value_type))
        return "Map({}, {}, {})".format(repr(self.key_type),
                                        repr(self.value_type),
                                        repr(self.key_cmp_functor))
