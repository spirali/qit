
from qit.build.env import CppEnv

class Qit:

    def __init__(self, debug=False):
        self.debug = debug
        self.env = CppEnv(self)

    def print_all(self, collection):
        self.env.run_print_all(collection)
