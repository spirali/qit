from testutils import Qit

from qit.build.builder import CppBuilder
from qit import Range


def test_build_range():
    r = Range(10)
    builder = CppBuilder(Qit())
    i = r.iterate()

    v = i.make_iterator(builder)
    t = i.get_iterator_type(builder)

    assert "{} {}(10);\n".format(t, v) == builder.writer.get_string()
