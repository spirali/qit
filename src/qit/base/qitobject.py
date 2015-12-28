from qit.base.eqmixin import HashableEqMixin
from qit.base.exception import InvalidType, QitException
from copy import copy

class QitObject(HashableEqMixin):

    childs = ()
    bounded_variables = frozenset()

    _name = None

    @property
    def name(self):
        if self._name is None:
            return type(self).__name__
        else:
            return self._name

    @name.setter
    def name(self, value):
        assert value is None or \
               isinstance(value, tuple) or \
               isinstance(value, str)
        if isinstance(value, tuple):
            value = "_".join(s if isinstance(s, str) else s.name
                             for s in value)
        self._name = value

    def is_type(self):
        return False

    def is_function(self):
        return False

    def is_variable(self):
        return False

    def is_expression(self):
        return False

    def as_type(self):
        raise QitException("'{}' cannot be used as type.".format(self))

    def get_objects(self):
        result = frozenset((self,))
        for child in self.childs:
            result = result.union(child.get_objects())
        return result

    def get_variables(self):
        result = frozenset()
        for child in self.childs:
            result = result.union(child.get_variables())
        return result.difference(self.bounded_variables)

    def get_functions(self):
        return [ obj for obj in self.get_objects()
                 if obj.is_function() ]

    def check_expression_type(self, type):
        if not self.is_expression():
            raise QitException("{} is not an expression.".format(self))
        if self.type != type:
            raise QitException(
                    "{} is not an expression of type {} but {}"
                            .format(self, type, self.type))

    def declare(self, builder):
        pass

    def declare_all(self, builder):
        for child in self.childs:
            child.declare_all(builder)
        self.declare(builder)

    def copy(self):
        return copy(self)


def check_qit_object(obj):
    if not isinstance(obj, QitObject):
        raise InvalidType(obj, "QitObject")


def fill_names(name_dict):
    for name, obj in name_dict.items():
        if isinstance(obj, QitObject):
            obj.name = name
