
from qit.base.type import Type

class File(Type):

    pass_by_value = True

    def build(self, builder):
        return "FILE*"


