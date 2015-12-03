
from qit.base.type import Type

class Struct(Type):

    autoname_prefix = "Struct"

    def __init__(self, *args):
        self.name = None
        names = []
        types = []

        for arg in args:
            if isinstance(arg, tuple) and len(arg) == 2:
                types.append(arg[0])
                names.append(arg[1])
            else:
                types.append(arg)
                names.append("v{}".format(len(names)))

        assert len(set(names)) == len(names)
        self.names = tuple(names)
        self.types = tuple(types)
        self.generators = (None,) * len(names)
        self.iterators = (None,) * len(names)

    @property
    def childs(self):
        return self.types

    def set_name(self, name):
        self.name = name
        return self

    def build_constant(self, builder, value):
        return builder.build_struct_constant(self, value)

    def is_python_instance(self, obj):
        return isinstance(obj, tuple) and len(obj) == len(self.names)

    def transform_python_instance(self, obj):
        return tuple(t.value(v) for t, v in zip(self.types, obj))

    def childs_from_value(self, value):
        return value

    def declare(self, builder):
        builder.declare_struct(self)

    def read(self, f):
        if not self.names:
            return ()
        lst = []
        for t in self.types:
            element = t.read(f)
            if element is None:
                if not lst:
                    return None # First element
                else:
                    raise Exception("Incomplete struct")
            lst.append(element)
        return tuple(lst)

    def __mul__(self, other):
        args = list(zip(self.types, self.names))
        args.append(other)
        return Struct(*args)

    def __repr__(self):
        return "Struct({})".format(
                ", ".join("({}, {})".format(repr(t), repr(name))
                for t, name in zip(self.types, self.names)))
