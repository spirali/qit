
from qit.build.env import CppEnv

class Context:

    def __init__(self):
        self.env = CppEnv()
        pass

    def print_all(self, collection):
        self.env.run_print_all(collection)
