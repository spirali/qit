
from qit.base.function import Function
from qit.base.int import Int
from qit.domains.iterator import Iterator
from qit.domains.domain import Domain
from qit.functions.random import rand_int

class Values(Domain):

    def __init__(self, type, values):
        values = tuple(type.value(v) for v in values)
        iterator = ValuesIterator(type, values)

        generator = Function().returns(type)
        generator.code("""
            switch({{rand_int}}(0, {{_size}})) {
                {%- for i, v in _values %}
                case {{i}}: return {{b(v)}};
                {%- endfor %}
                default: assert(0);
            }
        """, _values=enumerate(values), _size=len(values), rand_int=rand_int)
        generator.uses(values)

        super().__init__(type, iterator, generator())


class ValuesIterator(Iterator):

    def __init__(self, type, values):
        itype = Int()
        super().__init__(itype, type)
        self.reset_fn.code("iter = 0;")
        self.next_fn.code("iter++;")
        self.is_valid_fn.code("return iter < {{_size}};", _size=len(values))
        self.value_fn.code("""
            switch(iter) {
                {%- for v in _values %}
                case {{loop.index0}}: return {{b(v)}};
                {%- endfor %}
                default: assert(0);
            }
        """, _values=values).uses(values)
