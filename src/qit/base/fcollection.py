
from qit.base.collection import Collection
from qit.base.transformation import RandomTranformation


class FullCollection(Collection):

    def random(self):
        return RandomTranformation(self)
