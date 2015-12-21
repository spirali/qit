from qit.base.union import Union
from qit.domains.domain import Domain
from qit.domains.iterator import Iterator
from qit.functions.int import addition_n

class Join(Domain):

    def __init__(self, *domains):
        assert domains
        type = domains[0].type
        assert (d.type == type for d in domains)

        iterator = None
        size = None
        generator = None

        if all(d.iterator for d in domains):
            iterator = JoinIterator(domains)

        if all(d.size for d in domains):
            size = addition_n(len(domains))(*(d.size for d in domains))

        super().__init__(type, iterator, generator, size)
        self.domains = tuple(domains)

    def __add__(self, other):
        return Join(*(self.domains + (other,)))


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
