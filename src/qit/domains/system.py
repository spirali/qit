from qit.base.vector import Vector
from qit.base.set import Set
from qit.base.struct import Struct, KeyValue
from qit.base.int import Int
from qit.base.qitobject import QitObject
from qit.domains.iterator import Iterator
from qit.domains.domain import Domain


class SystemRule:

    def __init__(self, system, function):
        self.function = function
        if system.state_type == function.return_type:
            self.rule_type = 0
        elif Vector(system.state_type) == function.return_type:
            self.rule_type = 1
        else:
            assert 0


class System(QitObject):

    def __init__(self, initial_states, rules):
        self.state_iterator = initial_states.iterate()
        self.state_type = self.state_iterator.element_type
        self.rules = tuple(SystemRule(self, rule) for rule in rules)

    @property
    def state_depth_type(self):
        return KeyValue(self.state_type, Int())

    def states(self, depth, return_depth=False):
        return Domain(self.state_type,
                      iterator=StateIterator(self, depth, return_depth))


class StateIterator(Iterator):

    def __init__(self, system, depth, return_depth):
        state_type = system.state_type
        if return_depth:
            element_type = system.state_depth_type
        else:
            element_type = state_type

        depth = Int().value(depth)
        itype = Struct((Vector(state_type), "current"),
                       (Vector(state_type), "next"),
                       (Int(), "new_count"),
                       (Int(), "rule"),
                       (Set(state_type), "found_states"),
                       (Int(), "depth"))
        super().__init__(itype, element_type)

        functions = tuple(rule.function for rule in system.rules)

        self.reset_fn.code("""
            iter.rule = 0;
            iter.depth = 0;
            iter.current.clear();
            iter.next = {{vector}};
            iter.new_count = iter.next.size();
            iter.found_states.clear();
            for (auto const &state : iter.next) {
                iter.found_states.insert(state);
            }
        """, vector=system.state_iterator.to_vector())

        self.next_fn.code("""
            iter.new_count--;
            if (iter.new_count > 0) {
                return;
            }
            for(;;) {
                if (iter.current.size() == 0) {
                    if (iter.next.size() == 0) {
                        return;
                    }
                    if (iter.depth >= {{depth}}) {
                        return;
                    }
                    iter.depth++;
                    std::swap(iter.current, iter.next);
                }
                switch(iter.rule) {
                {%- for rule in _rules %}
                case {{loop.index0}}: {
                    iter.rule++;
                    {%- if rule.rule_type == 0 %}
                    {{state}} s = {{b(rule.function)}}(iter.current[iter.current.size()-1]);
                    if (iter.found_states.find(s) == iter.found_states.end()) {
                        iter.found_states.insert(s);
                        iter.next.push_back(s);
                        iter.new_count = 1;
                        return;
                    }
                    {%- endif %}
                    {%- if rule.rule_type == 1 %}
                    {{states}} v = {{b(rule.function)}}(iter.current[iter.current.size()-1]);
                    for (const auto &s : v) {
                        if (iter.found_states.find(s) == iter.found_states.end()) {
                            iter.found_states.insert(s);
                            iter.next.push_back(s);
                            iter.new_count++;
                        }
                    }
                    if (iter.new_count > 0) {
                        return;
                    }
                    {%- endif %}
                    }
                {%- endfor %}
                    default:
                       iter.rule = 0;
                       iter.current.pop_back();
                }
            }
        """, _rules=system.rules,
             depth=depth,
             state=state_type,
             states=Vector(state_type)).uses(functions)

        self.is_valid_fn.code("return iter.new_count;")
        if return_depth:
            self.value_fn.code(
                "return { iter.next[iter.next.size() - iter.new_count], iter.depth };")
        else:
            self.value_fn.code(
                "return iter.next[iter.next.size() - iter.new_count];")
