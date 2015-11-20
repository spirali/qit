
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
