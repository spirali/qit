
class Action:

    def __init__(self, iterator):
        self.iterator = iterator


class ActionPrintAll(Action):

    def run(self, env):
        return env.run_print_all(self.iterator)


class ActionCollect(Action):

    def run(self, env):
        return env.run_collect(self.iterator)
