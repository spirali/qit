
from qit.base.qitobject import QitObject, check_qit_object
from qit.base.atom import Constant


class Type(QitObject):

    def __init__(self):
        pass

    def is_type(self):
        return True

    def build_type(self, builder):
        return builder.get_autoname(self, "Type")

    def declare(self, builder):
        pass

    def is_python_instance(self, obj):
        return False

    def transform_python_instance(self, obj):
        return obj

    def check_value(self, value):
        if self.is_python_instance(value):
            return Constant(self, self.transform_python_instance(value))
        check_qit_object(value)
        value.check_expression_type(self)
        return value

    def const(self, value):
        assert self.is_python_instance(value)
        return Constant(self, self.transform_python_instance(value))

    def values(self, *args):
        from qit.base.values import Values
        return Values(self, args)

    def make_domain(self):
        from qit.base.domain import Domain
        return Domain(self)

    def __mul__(self, other):
        return Struct(self, other)


class NamedType(Type):

    def declare(self, builder):
        if self.name:
            self.basic_type.declare(builder)
            builder.declare_type_alias(self)

from qit.base.struct import Struct
