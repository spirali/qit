
class Function:

    def __init__(self, name):
        self.name = name
        self.params = []
        self.return_type = None
        self.inline_code = None
        self.external_file = None

    def takes(self, collection, name):
        self.params.append((collection, name))
        return self

    def returns(self, return_type):
        self.return_type = return_type
        return self

    def code(self, code):
        self.inline_code = code
        self.external_file = None
        return self

    def from_file(self, file_path):
        import os.path
        self.external_file = os.path.abspath(file_path)
        return self

    def is_external(self):
        return self.external_file is not None

    def declare(self, builder):
        builder.declare_function(self)

    def get_functions(self):
        fn_set = set()
        fn_set.add(self)
        return fn_set