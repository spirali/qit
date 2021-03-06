
from qit.base.function import Function
from qit.base.int import Int

rand_int = Function("rand_int")
rand_int.takes(Int(), "from").takes(Int(), "to")
rand_int.returns(Int())
rand_int.code("return std::uniform_int_distribution<qint>(from, to - 1)(QIT_GENERATOR);")
