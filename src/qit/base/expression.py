
from qit.base.qitobject import QitObject


class Expression(QitObject):

    def __init__(self, type):
        self.type = type

    def is_expression(self):
        return True
