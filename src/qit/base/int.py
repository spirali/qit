
from qit.base.type import BasicType


class Int(BasicType):

    def get_element_type(self, builder):
        return builder.get_int_type()

    @property
    def iterator(self):
        raise NotImplemented()

    @property
    def generator(self):
        raise NotImplemented()
