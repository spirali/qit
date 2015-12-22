from qit.base.int import Int
from qit.base.union import Union
from qit.base.function import Function
from qit.domains.domain import Domain
from qit.domains.iterator import Iterator
from qit.functions.int import addition_n
from qit.functions.random import rand_int

class Join(Domain):

    def __init__(self, domains, ratios=None):
        domains = tuple(domains)
        assert domains
        type = domains[0].type
        assert (d.type == type for d in domains)

        if ratios is not None:
            assert len(ratios) == len(domains)
        else:
            ratios = [1] * len(domains)

        ratios = tuple(Int().value(r) for r in ratios)

        iterator = None
        size = None
        generator = None

        if all(d.is_iterable() for d in domains):
            iterator = JoinIterator(domains)

        if all(d.size for d in domains):
            size = addition_n(len(domains))(*(d.size for d in domains))

        if all(d.is_generable() for d in domains):
            generator = self._make_generator(type, domains, ratios)

        super().__init__(type, iterator, generator, size)
        self.domains = domains
        self.ratios = ratios

    def _make_generator(self, type, domains, ratios):
        generators = tuple(d.generator for d in domains)
        f = Function(returns=type)
        f.code("""
            qint s = 0;
            {%- for r in _ratios %}
            s += {{b(r)}};
            {%- if not loop.last %}
            qint r{{loop.index0}} = s;
            {%- endif %}
            {%- endfor %}
            qint r = {{rand_int}}(0, s);
            {%- for g in _generators %}
                {%- if not loop.last %}
                if (r < r{{loop.index0}})
                {% endif %}
                {
                    return {{b(g)}};
                }
            {%- endfor %}
        """, _generators=generators, _ratios=ratios, rand_int=rand_int)
        f.uses(generators + ratios)
        return f()

    def __add__(self, other):
        size = other.size
        if size is None:
            size = 1
        return Join(self.domains + (other,), self.ratios + (size,))


class JoinIterator(Iterator):

    def __init__(self, domains):
        type = domains[0].type
        iterators = tuple(d.iterator for d in domains)
        itypes = tuple(i.itype for i in iterators)
        itype = Union(itypes + (None,))
        uses = sum(tuple(i.childs for i in iterators), ())

        super().__init__(itype, type)

        self.reset_fn.code("""
            {%- for i in _iterators %}
                {
                    iter.set{{loop.index0}}();
                    auto &v = iter.get{{loop.index0}}();
                    {{b(i.reset_fn)}}(v);
                    if ({{b(i.is_valid_fn)}}(v)) {
                        return;
                    };
                }
            {%- endfor %}
                iter.set{{_iterators|length}}();
        """, _iterators=iterators).uses(uses)

        self.next_fn.code("""
            bool next = true;
            switch(iter.tag()) {
            {%- for i in _iterators %}
                case {{loop.index0}}: {
                    auto &v = iter.get{{loop.index0}}();
                    if (next) {
                        {{b(i.next_fn)}}(v);
                    }
                    if ({{b(i.is_valid_fn)}}(v)) {
                        return;
                    };
                    iter.set{{loop.index}}();
                    {%- if not loop.last %}
                    {{b(_iterators[loop.index].reset_fn)}}(iter.get{{loop.index}}());
                    next = false;
                    {%- endif %}
                }
            {%- endfor %}
            }
        """, _iterators=iterators).uses(uses)


        self.is_valid_fn.code("""
                return iter.tag() < {{_iterators|length}};
        """, _iterators=iterators)

        self.value_fn.code("""
            switch(iter.tag()) {
            {%- for i in _iterators %}
                case {{loop.index0}}:
                    return {{b(i.value_fn)}}(iter.get{{loop.index0}}());
            {%- endfor %}
                default: assert(0);
            }
        """, _iterators=iterators).uses(uses)
