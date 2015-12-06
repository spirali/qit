
class QitException(Exception):
    pass


class InvalidType(QitException):

    def __init__(self, obj, expected):
        super().__init__("{} is not {}".format(repr(obj), expected))


class MissingFiles(QitException):

    def __init__(self, message, filenames):
        super().__init__(message)
        self.filenames = filenames
