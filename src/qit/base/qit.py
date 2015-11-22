from qit.build.builder import CppBuilder
from qit.build.env import CppEnv


class Qit:

    def __init__(self,
                 debug=False,
                 build_dir="./qit-build"):
        self.debug = debug
        self.build_dir = build_dir
        self.env = CppEnv(self)

    def run(self, iterator):
        return self.env.run_collect(iterator)

    def declarations(self, obj, exclude_inline=False):
        if not hasattr(obj, "get_functions"):
            raise TypeError("Wrong type entered: " + str(obj))

        builder = CppBuilder(self)

        return [builder.get_function_declaration(fn) for fn in obj.get_functions()
                if (not exclude_inline or fn.is_external())]

    def create_source_files(self, obj):
        if not hasattr(obj, "get_functions"):
            raise TypeError("Wrong type entered: " + str(obj))

        builder = CppBuilder(self)
        builder.create_files(obj)
