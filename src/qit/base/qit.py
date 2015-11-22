from qit.build.builder import CppBuilder
from qit.build.env import CppEnv


class Qit:

    def __init__(self,
                 source_dir=".",
                 build_dir="./qit-build",
                 create_files=False,
                 debug=False):
        self.debug = debug
        self.source_dir = source_dir
        self.build_dir = build_dir
        self.auto_create_files = create_files
        self.env = CppEnv(self)

    def run(self, iterator):
        return self.env.run_collect(iterator)

    def declarations(self, obj, exclude_inline=True):
        if not hasattr(obj, "get_functions"):
            raise TypeError(
                    repr(obj) + " does not have attribute 'get_functions'")
        return self.env.declarations(obj, exclude_inline=exclude_inline)

    def create_files(self, obj):
        if not hasattr(obj, "get_functions"):
            raise TypeError(
                    repr(obj) + " does not have attribute 'get_functions'")
        self.env.create_source_files(obj)
