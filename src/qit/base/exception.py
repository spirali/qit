
class QitException(Exception):
    pass


class InvalidType(QitException):

    def __init__(self, obj, expected):
        super().__init__("{} is not {}".format(repr(obj), expected))


class InvalidAtomType(InvalidType):

    def __init__(self, type, obj):
        Exception.__init__(self, "{} is not a valid atom of type {}" \
                .format(repr(obj), repr(type)))


class InvalidConstant(InvalidAtomType):

    def __init__(self, type, obj):
        Exception.__init__(self, "{} is not a valid constant of type {}" \
                .format(repr(obj), repr(type)))


class MissingFiles(QitException):

    def __init__(self, message, filenames):
        super().__init__(message)
        self.filenames = filenames
