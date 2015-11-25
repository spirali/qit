from qit.base.iterator import Iterator
from qit.base.sequence import Sequence
from qit.base.int import Int
from enum import Enum

class RuleType(Enum):
    invalid = 0
    one_to_one = 1
    one_to_many = 2


class System:

    def __init__(self, initial_states, rules):
        self.initial_states_iterator = initial_states.iterator
        self.rules = tuple(rules)
        assert all(self.get_rule_type(rule) != RuleType.invalid
                   for rule in rules), "Invalid rules"

    @property
    def state_type(self):
        return self.initial_states_iterator.output_type.basic_type

    def iterate_states(self, depth):
        return SystemIterator(self, depth)

    def get_rule_type(self, rule):
        rule_type = rule.return_type.basic_type
        basic_type = self.state_type
        if basic_type == rule_type:
            return RuleType.one_to_one
        elif Sequence(basic_type) == rule_type:
            return RuleType.one_to_many
        return RuleType.invalid


class SystemIterator(Iterator):

    def __init__(self, system, depth):
        super().__init__(system.state_type)
        self.system = system
        self.depth = Int().check_value(depth)

    @property
    def childs(self):
        return super().childs + \
               (self.system.initial_states_iterator, self.depth) + \
               self.system.rules

    def get_iterator_type(self, builder):
        return builder.get_system_iterator_type(self)

    def make_iterator(self, builder):
        return builder.make_basic_iterator(
                self, (self.system.initial_states_iterator,))

    def declare(self, builder):
        builder.declare_system_iterator(self)
