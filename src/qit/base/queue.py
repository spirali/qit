from qit.base.int import Int
from qit.base.vector import Vector

class Queue(Vector):

    def build(self, builder):
        return "std::deque<{} >".format(self.element_type.build(builder))

    def build_destructor(self, builder):
        return "~deque<{} >".format(self.element_type.build(builder))

    def __repr(self):
        return "Queue({})".format(repr(self.element_type))
