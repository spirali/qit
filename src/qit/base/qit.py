
from qit.build.env import CppEnv

class Qit:

    def __init__(self, debug=False):
        self.debug = debug
        self.env = CppEnv(self)

    def run(self, action):
        return action.run(self.env)
