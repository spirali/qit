
from qit.build.builder import CppBuilder
from qit.base.type import Range


def test_build_range():
    r = Range(10)
    builder = CppBuilder()
    v = r.make_iterator(builder)
    assert "qit::RangeIterator {}(10);\n".format(v) == builder.writer.get_string()
