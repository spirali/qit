
from qit.base.qitobject import QitObject, check_qit_object
from qit.base.constructor import Constructor


class Type(QitObject):

    autoname_prefix = "Type"
    pass_by_value = False

    def __init__(self):
        pass

    def is_type(self):
        return True

    def build(self, builder):
        return builder.get_autoname(self)

    def declare(self, builder):
        pass

    def is_python_instance(self, obj):
        return False

    def transform_python_instance(self, obj):
        return obj

    def value(self, value):
        if self.is_python_instance(value):
            return Constructor(self, self.transform_python_instance(value))
        check_qit_object(value)
        value.check_expression_type(self)
        return value

    def childs_from_value(self, value):
        return ()

    def values(self, *args):
        from qit.base.values import Values
        return Values(self, args)

    def prepare_write_function(self):
        from qit.base.function import Function
        from qit.base.file import File
        return Function().takes(File(), "output").takes(self, "value")

    def build_param(self, builder, name):
        if self.pass_by_value:
            return "{} {}".format(self.build(builder), name)
        else:
            return "const {} &{}".format(self.build(builder), name)

    def __mul__(self, other):
        return Struct(self, other)


from qit.base.struct import Struct
