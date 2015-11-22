
class QitException(Exception):
    pass

class MissingFiles(QitException):

    def __init__(self, message, filenames):
        super().__init__(message)
        self.filenames = filenames
