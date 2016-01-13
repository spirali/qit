import sys
sys.path.insert(0, "../src")

from qit import Qit, Map, Int, Mapping, System, Set, Struct, Product, Variable, Range, Join, Function, System, Vector, Values, Bool, Sequence, Class, KeyValue, ActionSystem

# N_EVENTS, MAX_IN_ARC_WEIGHT, MAX_OUT_ARC_WEIGHT, MAX_PLACE_MARKING = (2, 1, 1, 1)
# DEPTH = 3
N_EVENTS, MAX_IN_ARC_WEIGHT, MAX_OUT_ARC_WEIGHT, MAX_PLACE_MARKING = (3, 2, 2, 2)
DEPTH = 6

# Petri net definition
P = Range(N_EVENTS)
T = Range(N_EVENTS)
I = Product((P, "place"), (T, "transition"))
O = Product((T, "transition"), (P, "place"))

Wi = Mapping(I, Range(MAX_IN_ARC_WEIGHT + 1))  # weights of input arcs
Wo = Mapping(O, Range(MAX_OUT_ARC_WEIGHT + 1)) # weights of output arcs
M0 = Mapping(P, Range(MAX_PLACE_MARKING + 1))      # mapping functions

################################################################################

ctx = Qit(debug=True)

v_marking = M0.variable("mapping")
v_input_arcs = Wi.variable("input_arcs")
v_output_arcs = Wo.variable("output_arcs")

t_marking = M0.as_type()
t_iarcs = Wi.as_type()

fs_enabled = tuple(
     Function("t{}_is_enabled".format(t)).takes(t_marking, "marking").takes(t_iarcs, "input_arcs").returns(Bool()).code("""
        for (auto it = input_arcs.begin(); it != input_arcs.end(); it++) {
            if (it->first.transition == {{tid}} &&
                it->second > marking.at(it->first.place)) {
                return false;
            }
        }
        return true;
     """, tid=Int().value(t))
     for t in range(N_EVENTS))

fs_fire = tuple(
    Function("t{}".format(t)).takes(t_marking, "marking").reads(v_input_arcs, v_output_arcs).returns(Vector(t_marking)).code("""
        if ({{is_enabled}}(marking, input_arcs)) {
            {{t_marking}} new_marking(marking);
            for (auto it = input_arcs.begin(); it != input_arcs.end(); it++) {
                if (it->first.transition == {{tid}}) {
                    new_marking[it->first.place] -= it->second;
                }
            }
            for (auto it = output_arcs.begin(); it != output_arcs.end(); it++) {
                if (it->first.transition == {{tid}}) {
                    new_marking[it->first.place] += it->second;
                }
            }
            return {new_marking};
        }
        return {};
    """, is_enabled=fs_enabled[t], t_marking=t_marking, tid=Int().value(t))
    for t in range(N_EVENTS))

statespace = ActionSystem(Values(t_marking, [v_marking]), fs_fire)
states = statespace.states(DEPTH)
f_states = states.iterate().make_function((v_marking, v_input_arcs, v_output_arcs))

init_values = Product((M0, "init_marking"), (Wi, "input"), (Wo, "output"))

t_element = statespace.sas_type
t_states = Vector(t_element)
t_input = init_values.as_type()
t_result = Struct((init_values, "init_values"), (t_states, "lts"))

f_process_input = Function("map_variables").takes(init_values, "init_values").returns(t_result)
f_process_input.code("""
    return {{t_result}}(init_values, {{f_states}}(init_values.init_marking, init_values.input, init_values.output));
""", f_states=f_states, t_result=t_result,)


f_eq_states = Function("eq_states").takes(t_element, "s1").takes(t_element, "s2").returns(Bool())
f_eq_states.code("""
    return s1.s1_id == s2.s1_id && s1.action == s2.action && s1.s2_id == s2.s2_id;
""")

input_lts = t_states.value([t_element.value((1, "t0", 2)),
                            t_element.value((2, "t0", 3)),
                            t_element.value((3, "t1", 4)),
                            t_element.value((4, "t1", 5)),
                            t_element.value((5, "t2", 6)),
                            t_element.value((6, "t2", 1))])

# input_lts = t_states.value([t_element.value((1, "t0", 2)),
                            # t_element.value((2, "t1", 1))])

f_eq_statespaces = Function("eq_statespaces").takes(t_result, "result").returns(Bool())
f_eq_statespaces.code("""
        {{t_lts}} lts1 = result.lts;
        {{t_lts}} lts2 = {{lts2}};
        if (lts1.size() != lts2.size()) {
            return false;
        }

        for (int i = 0; i < lts1.size(); i++) {
            if (!{{eq_states}}(lts1[i], lts2[i])) {
                return false;
            }
        }
        return true;
""", eq_states=f_eq_states, lts2=input_lts, t_lts=t_states)

# solution = t_input.value(({0: 1, 1: 0}, {(0, 1): 0, (1, 0): 0, (0, 0): 1, (1, 1): 1}, {(0, 1): 1, (1, 0): 1, (0, 0): 0, (1, 1): 0})) # t0 -> t1 ->t0 -> ...
# res = ctx.run(t_input.values(solution).iterate().map(f_map_variables))

# solution = t_input.value(( # triangle t0 -> t0 -> t1 -> t1 -> t2 -> t2 -> t0 -> ...
    # {0: 2, 1: 0, 2: 2},
    # {
        # (0, 0): 2,
        # (0, 1): 1,
        # (0, 2): 0,
        # (1, 0): 0,
        # (1, 1): 2,
        # (1, 2): 1,
        # (2, 0): 1,
        # (2, 1): 0,
        # (2, 2): 2

    # },
    # {
        # (0, 0): 2,
        # (0, 1): 1,
        # (0, 2): 0,
        # (1, 0): 0,
        # (1, 1): 2,
        # (1, 2): 1,
        # (2, 0): 1,
        # (2, 1): 0,
        # (2, 2): 2
    # }))
# res = ctx.run(t_input.values(solution).iterate().map(f_map_variables))

empty_value = t_result.value((({}, {}, {}), []))
res = ctx.run(init_values.iterate().map(f_process_input).filter(f_eq_statespaces).first(empty_value))
print ("Result: ", res)
