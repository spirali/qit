
from qit.base.expression import Expression


class Constructor(Expression):

    def __init__(self, type, value):
        super().__init__(type)
        self.value = value

    def build(self, builder):
        return self.type.build_value(builder, self.value)

    def is_constructor(self):
        return True

    @property
    def childs(self):
        return (self.type,) + self.type.childs_from_value(self.value)

    def __repr__(self):
        return "Constructor({}, {})".format(self.type, repr(self.value))
