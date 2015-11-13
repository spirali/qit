
from qit.base.iterator import Iterator


class Transformation(Iterator):

    def __init__(self, iterator):
        self.parent_iterator = iterator

    @property
    def output_type(self):
        return self.parent_iterator.output_type

    def declare(self, builder):
        self.parent_iterator.declare(builder)

    def make_iterator(self, builder):
        return builder.make_basic_iterator(self, (self.parent_iterator,))

    def get_element_type(self, builder):
        return self.parent_iterator.get_element_type(builder)


class TakeTransformation(Transformation):

    def __init__(self, parent_iterator, count):
        super().__init__(parent_iterator)
        self.count = count

    def get_iterator_type(self, builder):
        return builder.get_take_iterator(self)

    def make_iterator(self, builder):
        return builder.make_basic_iterator(self,
                                           (self.parent_iterator,),
                                           (str(self.count),))


class MapTransformation(Transformation):

    def __init__(self, iterator, function):
        super().__init__(iterator)
        self.function = function
        assert function.return_type is not None
        # TODO: Check compatability of function and valid return type

    @property
    def output_type(self):
        return self.function.return_type

    def declare(self, builder):
        self.parent_iterator.declare(builder)
        self.function.return_type.declare(builder)
        self.function.declare(builder)

    def get_iterator_type(self, builder):
        return builder.get_map_iterator(self)

    def get_element_type(self, builder):
        return self.function.return_type.get_element_type(builder)
