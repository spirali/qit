from qit.base.iterator import Iterator
from qit.base.int import Int

class Transformation(Iterator):

    def __init__(self, iterator, output_type=None):
        if output_type is None:
            output_type = iterator.output_type
        super().__init__(output_type)
        self.parent_iterator = iterator

    def make_iterator(self, builder):
        return builder.make_basic_iterator(self, (self.parent_iterator,))

    def get_element_type(self, builder):
        return self.parent_iterator.get_element_type(builder)

    @property
    def childs(self):
        return (self.parent_iterator,)


class TakeTransformation(Transformation):

    def __init__(self, parent_iterator, count):
        super().__init__(parent_iterator)
        self.count = Int().check_value(count)

    def get_iterator_type(self, builder):
        return builder.get_take_iterator(self)

    def make_iterator(self, builder):
        return builder.make_basic_iterator(self,
                                          (self.parent_iterator,),
                                          (self.count.get_code(builder),))

    @property
    def childs(self):
        return super().childs + (self.count,)


class MapTransformation(Transformation):

    def __init__(self, iterator, function):
        super().__init__(iterator, function.return_type)
        self.function = function
        assert function.return_type is not None
        # TODO: Check compatibility of function and valid return type

    def make_iterator(self, builder):
        fn = self.function.make_functor(builder)
        return builder.make_basic_iterator(
                self, (self.parent_iterator,), (fn,))

    def get_iterator_type(self, builder):
        return builder.get_map_iterator(self)

    def get_element_type(self, builder):
        return self.function.return_type.get_element_type(builder)

    @property
    def childs(self):
        return super().childs + (self.function,)


class SortTransformation(Transformation):

    def __init__(self, iterator, ascending=True):
        super().__init__(iterator)
        self.asceding = True

    def get_iterator_type(self, builder):
        return builder.get_sort_iterator(self)

class FilterTransformation(Transformation):

    def __init__(self, iterator, function):
        super().__init__(iterator)
        self.function = function

        from qit import Bool

        assert isinstance(function.return_type, Bool)
        # TODO: Check compatibility of function parameters

    def get_iterator_type(self, builder):
        return builder.get_filter_iterator(self)

    def get_element_type(self, builder):
        return self.function.return_type.get_element_type(builder)

    @property
    def childs(self):
        return super().childs + (self.function,)
