from qit.base.iterator import IteratorType
from qit.base.vector import Vector
from qit.base.int import Int
from qit.base.qitobject import QitObject
from qit.base.utils import sorted_variables
from enum import Enum

class RuleType(Enum):
    invalid = 0
    one_to_one = 1
    one_to_many = 2


class System(QitObject):

    def __init__(self, initial_states, rules):
        self.state_iterator = initial_states.iterate()
        self.state_type = self.state_iterator.type.output_type
        self.rules = tuple(rules)
        assert all(self.get_rule_type(rule) != RuleType.invalid
                   for rule in rules), "Invalid rules"

    @property
    def childs(self):
        return (self.state_type, self.state_iterator) + self.rules

    def iterate_states(self, depth):
        return SystemIterator(self, depth).make()

    def get_rule_type(self, rule):
        rule_type = rule.return_type
        if self.state_type == rule_type:
            return RuleType.one_to_one
        elif Vector(self.state_type) == rule_type:
            return RuleType.one_to_many
        return RuleType.invalid


class SystemIterator(IteratorType):

    def __init__(self, system, depth):
        super().__init__(system.state_type)
        self.depth = Int().check_value(depth)
        self.system = system

    @property
    def childs(self):
        return super().childs + (self.depth, self.system)

    @property
    def constructor_args(self):
        variables = sorted_variables(self.get_variables())
        return (self.system.state_iterator, self.depth) + tuple(variables)

    def declare(self, builder):
        builder.declare_system_iterator(self)
