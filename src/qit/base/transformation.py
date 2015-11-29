from qit.base.iterator import IteratorType
from qit.base.int import Int


class Transformation(IteratorType):

    def __init__(self, iterator, output_type=None):
        if output_type is None:
            output_type = iterator.type.output_type
        super().__init__(output_type)
        self.parent_iterator = iterator

    @property
    def childs(self):
        return super().childs + (self.parent_iterator,)

    @property
    def constructor_args(self):
        return (self.parent_iterator,)


class TakeTransformation(Transformation):

    def __init__(self, parent_iterator, count):
        super().__init__(parent_iterator)
        self.count = Int().check_value(count)

    def build_type(self, builder):
        return builder.build_take_iterator(self)

    @property
    def constructor_args(self):
        return (self.parent_iterator, self.count)

    @property
    def childs(self):
        return super().childs + (self.count,)


class MapTransformation(Transformation):

    def __init__(self, iterator, function):
        super().__init__(iterator, function.return_type)
        self.function = function
        assert function.return_type is not None
        # TODO: Check compatibility of function and valid return type

    def build_type(self, builder):
        return builder.build_map_iterator(self)

    @property
    def constructor_args(self):
        return (self.parent_iterator, self.function)

    @property
    def childs(self):
        return super().childs + (self.function,)


class SortTransformation(Transformation):

    def __init__(self, iterator, ascending=True):
        super().__init__(iterator)
        self.asceding = True

    def build_type(self, builder):
        return builder.build_sort_iterator(self)


class FilterTransformation(Transformation):

    def __init__(self, iterator, function):
        super().__init__(iterator)
        self.function = function

    def build_type(self, builder):
        return builder.build_filter_iterator(self)

    @property
    def constructor_args(self):
        return (self.parent_iterator, self.function)

    @property
    def childs(self):
        return super().childs + (self.function,)
