from qit.base.type import Type
from qit.base.int import Int
import collections

class Set(Type):

    def __init__(self, element_type):
        super().__init__()
        self.element_type = element_type

    @property
    def childs(self):
        return super().childs + (self.element_type,)

    def build(self, builder):
        return "std::set<{} >".format(
            self.element_type.build(builder))

    def build_destructor(self, builder):
        return "~set<{} >".format(
            self.element_type.build(builder))

    def read(self, f):
        size = Int().read(f)
        if size is None:
            return None
        return set(self.element_type.read(f) for i in range(size))

    def childs_from_value(self, value):
        return value

    @property
    def write_function(self):
        f = self.prepare_write_function()
        f.code("""
        {{write_int}}(output, value.size());
        for (auto const & item : value) {
            {{write_function}}(output, item);
        }
        """, write_int=Int().write_function,
             write_function=self.element_type.write_function)
        return f

    def build_value(self, builder, value):
        args = ",".join(v.build(builder) for v in value)
        return "{{ {} }}".format(args)

    def is_python_instance(self, obj):
        return isinstance(obj, collections.Iterable)

    def transform_python_instance(self, obj):
        return tuple(self.element_type.value(v) for v in obj)
