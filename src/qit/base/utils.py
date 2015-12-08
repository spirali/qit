
import os
from qit.base.exception import QitException

def sorted_variables(variables):
    return sorted(variables, key=lambda v: v.name)

def validate_variables(variables):
    tmp = list(variables)
    tmp.sort(key=lambda v: v.name)
    for i, v in enumerate(tmp[:-1]):
        if v.name == tmp[i+1].name:
            raise QitException(
                    "Variable '{0}.name' was used with two different types:"
                    "{0.type} and {1.type}".format(v, tmp[i+1]))

def assign_values(variables, args):
    result = {}
    for v in variables:
        value = args.get(v.name)
        if value is None:
            raise QitException("Unbound variable {}".format(v.name))
        result[v] = v.type.value(args[v.name])
    return result

def is_valid_name(value):
    if not isinstance(value, str) or len(value) == 0:
        return False
    if not value[0].isalpha() and value[0] != "_":
        return False
    return all(c.isalnum() or value == "_" for c in value)

def makedir_if_not_exists(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
