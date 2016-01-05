from qit.base.vector import Vector
from qit.base.set import Set
from qit.base.struct import Struct, KeyValue
from qit.base.int import Int
from qit.base.bool import Bool
from qit.base.enum import Enum
from qit.base.map import Map
from qit.base.function import Function, Functor
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
        iterator = StateIterator(self, depth, return_depth)
        return Domain(iterator.element_type, iterator)


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

class ActionSystem(System):

    def __init__(self,
                 initial_states,
                 rules,
                 eq_states_fn = None,
                 cmp_states_fn=None):
        super().__init__(initial_states, rules)
        self.eq_states_fn = eq_states_fn
        self.cmp_states_fn = cmp_states_fn
        self.action_names = Enum(*(rule.name for rule in rules))

    @property
    def sas_type(self):
        return Struct((Int(), "s1_id"),
                      (self.action_names, "action"),
                      (Int(), "s2_id"))

    @property
    def sas_depth_type(self):
        return KeyValue(self.sas_type, Int())

    def states(self, depth, return_depth=False):
        iterator = ActionStateIterator(self, depth, return_depth)
        return Domain(iterator.element_type, iterator)

class ActionStateIterator(Iterator):

    def __init__(self, system, depth, return_depth):
        state_type = system.state_type
        sas_type = system.sas_type
        if return_depth:
            element_type = system.sas_depth_type
        else:
            element_type = sas_type

        eq_states_fn = system.eq_states_fn
        if eq_states_fn is None:
            eq_states_fn = Function("eq_states").takes(state_type, "s1")\
                                                .takes(state_type, "s2")\
                                                .returns(Bool())
            eq_states_fn.code("return s1 == s2;")

        cmp_states_fn = system.cmp_states_fn
        if cmp_states_fn is None:
            cmp_states_fn = Function("compare_states").takes(state_type, "s1")\
                                                      .takes(state_type, "s2")\
                                                      .returns(Bool())
            cmp_states_fn.code("return s1 < s2;")

        depth = Int().value(depth)
        state_ids_type = Map(state_type, Int(), cmp_states_fn)
        itype = Struct((state_ids_type,     "state_ids"),
                       (Vector(state_type), "current"),
                       (Vector(state_type), "next"),
                       (Vector(sas_type),   "buff_values"),
                       (sas_type,           "value"),
                       (Int(),              "rule"),
                       (Int(),              "depth"),
                       (Int(),              "gen_state_id"))
        super().__init__(itype, element_type)

        functions = tuple(rule.function for rule in system.rules)

        action_type1  = None
        action_type2  = None
        new_value_fn  = None
        new_values_fn = None

        if functions:
            action_type1 = Functor("atype1", state_type, (state_type, "s"))
            new_value_fn = Function("compute_new_value")\
                            .takes(itype, "iter", const=False)\
                            .takes(state_type, "current")\
                            .takes(system.action_names, "action_name")\
                            .takes(action_type1, "action_fn")\
                            .returns(Vector(sas_type))
            new_value_fn.code("""
                {{state}} new_state = action_fn(current);
                auto it = iter.state_ids.find(new_state);
                if (it == iter.state_ids.end()) {
                    iter.state_ids[new_state] = ++iter.gen_state_id;
                    iter.next.push_back(new_state);
                }
                return { {{sas}}(iter.state_ids[current], action_name, iter.state_ids[new_state]) };
            """, state=state_type,
                 sas=sas_type)

            action_type2 = Functor(
                    "atype1", Vector(state_type), (state_type, "s"))
            new_values_fn = Function("compute_new_values")\
                            .takes(itype, "iter", const=False)\
                            .takes(state_type, "current")\
                            .takes(system.action_names, "action_name")\
                            .takes(action_type2, "action_fn")\
                            .returns(Vector(sas_type))
            new_values_fn.code("""
                std::vector<{{sas}} > buff;
                std::vector<{{state}} > new_states = action_fn(current);
                for ({{state}} &s : new_states) {
                    auto s_it = iter.state_ids.find(s);
                    if (s_it == iter.state_ids.end()) {
                        iter.state_ids[s] = ++iter.gen_state_id;
                        iter.next.push_back(s);
                    }

                    {{sas}} value(iter.state_ids[current], action_name, iter.state_ids[s]);
                    auto sas_it = std::find(buff.begin(), buff.end(), value);
                    if (sas_it == buff.end()) {
                        buff.push_back(value);
                    }
                }

                std::reverse(buff.begin(), buff.end());
                return buff;
            """, state=state_type,
                 sas=sas_type)

            functions += (new_value_fn, new_values_fn)

        self.reset_fn.code("""
            iter.gen_state_id = 0;
            iter.rule = 0;
            iter.depth = 0;
            iter.state_ids = {{states_empty_map}};
            iter.current = {{vector}};
            if (iter.current.size() > 1) {
                std::sort(iter.current.begin(), iter.current.end());
                // same initial states are reducet to only one
                auto it = std::unique(iter.current.begin(), iter.current.end(), {{eq_states}});
                iter.current.resize(std::distance( iter.current.begin(), it));
            }
            for (auto &e : iter.current) {
                iter.state_ids[e] = ++iter.gen_state_id;
            }
            iter.next.clear();

            {# first call of the next function fills first values, if there are some #}
            {{next_fn}}(iter);
            if (iter.buff_values.size() == 0) {
                iter.current.clear();
            }
        """, vector=system.state_iterator.to_vector(),
             states_empty_map=state_ids_type.value( {} ),
             eq_states=eq_states_fn,
             next_fn=self.next_fn)

        self.next_fn.code("""
            {%- if _new_value is not none %}
            if (iter.buff_values.size() > 0) {
                iter.buff_values.pop_back(); // remove the previous one
                // set value if there is some
                if (iter.buff_values.size() > 0) {
                    iter.value = iter.buff_values[iter.buff_values.size()-1];
                    return;
                }
            }

            for (;;) {
                if (iter.current.size() == 0) {
                    if (iter.next.size() == 0 || iter.depth >= {{depth}}) {
                        iter.next.clear();
                        return;
                    }
                    iter.depth++;
                    std::swap(iter.current, iter.next);
                }

                switch(iter.rule) {
                {%- for rule in _rules %}
                case {{loop.index0}}: {
                    {# different functions for types one value and more values #}

                    {%- if rule.rule_type == 0 %}
                    iter.buff_values = {{b(_new_value)}}(
                        iter, iter.current[iter.current.size()-1],
                        {{action}}(iter.rule), {{b(rule.function)}});
                    {%- endif %}

                    {%- if rule.rule_type == 1 %}
                    iter.buff_values = {{b(_new_values)}}(
                        iter, iter.current[iter.current.size()-1],
                        {{action}}(iter.rule), {{b(rule.function)}});
                    {%- endif %}

                    iter.rule++;
                    if (iter.buff_values.size() > 0) {
                        iter.value = iter.buff_values[iter.buff_values.size()-1];
                        return;
                    }
                }
                {%- endfor %}
                default:
                    iter.rule = 0;
                    iter.current.pop_back();
                }
            }
            {%- endif %}
        """, _rules=system.rules,
             _new_value=new_value_fn,
             _new_values=new_values_fn,
             action=system.action_names,
             depth=depth).uses(functions)

        self.is_valid_fn.code("""
            return !(iter.current.size() == 0 && iter.next.size() == 0 && iter.buff_values.size() == 0);
        """)

        if return_depth:
            self.value_fn.code(
                "return { iter.value, iter.depth };")
        else:
            self.value_fn.code(
                "return iter.value;")
