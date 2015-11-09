
class Function:

    def __init__(self, name):
        self.name = name
        self.params = []
        self.return_type = None
        self.inline_code = None

    def takes(self, collection, name):
        self.params.append((collection, name))
        return self

    def returns(self, return_type):
        self.return_type = return_type
        return self

    def code(self, code):
        self.inline_code = code
        return self

    def declare(self, builder):
        builder.declare_function(self)
