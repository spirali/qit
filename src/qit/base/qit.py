
from qit.build.env import CppEnv

class Qit:

    def __init__(self, debug=False):
        self.debug = debug
        self.env = CppEnv(self)

    def run(self, iterator):
        return self.env.run_collect(iterator)
