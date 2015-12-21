from qit.base.int import Int
from qit.base.union import Union
from qit.base.map import Map
from qit.base.function import Function
from qit.domains.domain import Domain
from qit.domains.iterator import Iterator
from qit.functions.int import power


class Mapping(Domain):

    def __init__(self, key_domain, value_domain, choose_fn=None):
        assert not isinstance(value_domain, tuple) or choose_fn is not None
        assert key_domain.is_iterable()

        if isinstance(value_domain, Domain):
            self.init_simple_mapping(key_domain, value_domain)
        else:
            self.init_with_choose_fn(key_domain, value_domain, choose_fn)

    def init_simple_mapping(self, key_domain, value_domain):
        iterator = None
        generator = None
        size = None
        map_type = Map(key_domain.type, value_domain.type)
        if value_domain.is_iterable():
            iterator = MappingIterator(key_domain, value_domain)
        if value_domain.is_generable():
            generator = Function().returns(map_type).code("""
                {{type}} result;
                {{key_itype}} key_iterator;
                {{key_reset}}(key_iterator);
                while ({{key_is_valid}}(key_iterator)) {
                    result[{{key_value}}(key_iterator)] = {{generator}};
                    {{key_next}}(key_iterator);
                }
                return result;
            """, type=map_type,
                 key_itype=key_domain.iterator.itype,
                 key_reset=key_domain.iterator.reset_fn,
                 key_is_valid=key_domain.iterator.is_valid_fn,
                 key_next=key_domain.iterator.next_fn,
                 key_value=key_domain.iterator.value_fn,
                 generator=value_domain.generator)()
        if key_domain.size and value_domain.size:
            size = power(value_domain.size, key_domain.size)
        super().__init__(map_type, iterator, generator, size)


    def init_with_choose_fn(self, key_domain, value_domain, choose_fn):
        iterator = None
        generator = None
        size = None
        map_type = Map(key_domain.type, value_domain[0].type)
        assert choose_fn
        if all(d.is_iterable() for d in value_domain):
            iterator = MappingIterator2(
                key_domain, value_domain, choose_fn)

        sizes = tuple(d.size for d in value_domain)
        if key_domain.size and all(sizes):
            size = Function().returns(Int()).code("""
                {{b(_k.itype)}} key_iterator;
                {{b(_k.reset_fn)}}(key_iterator);
                int result = 1;
                while ({{b(_k.is_valid_fn)}}(key_iterator)) {
                    switch({{choose_fn}}({{b(_k.value_fn)}}(key_iterator))) {
                    {%- for i in _i %}
                    case {{loop.index0}}:
                        result *= {{b(_sizes[loop.index0])}};
                        break;
                    {%- endfor %}
                    default:
                        assert(0);
                    }
                    {{b(_k.next_fn)}}(key_iterator);
                }
                return result;
            """, choose_fn=choose_fn, _sizes=sizes,
                 _k=key_domain.iterator, _i=range(len(value_domain))) \
                    .uses(sizes + key_domain.iterator.childs)()

        generators = tuple(d.generator for d in value_domain)
        if all(generators):
            generator = Function().returns(map_type).code("""
                {{type}} result;
                {{key_itype}} key_iterator;
                {{key_reset}}(key_iterator);
                while ({{key_is_valid}}(key_iterator)) {
                    {{key_type}} key = {{key_value}}(key_iterator);
                    switch({{choose_fn}}(key)) {
                    {%- for g in _generators %}
                    case {{loop.index0}}:
                        result[key] = {{b(g)}};
                        break;
                    {%- endfor %}
                    default:
                        assert(0);
                    }
                    {{key_next}}(key_iterator);
                }
                return result;
            """, type=map_type,
                 choose_fn=choose_fn,
                 key_type=key_domain.type,
                 key_itype=key_domain.iterator.itype,
                 key_reset=key_domain.iterator.reset_fn,
                 key_is_valid=key_domain.iterator.is_valid_fn,
                 key_next=key_domain.iterator.next_fn,
                 key_value=key_domain.iterator.value_fn,
                 _generators=generators).uses(generators)()
        super().__init__(map_type, iterator, generator, size)


class MappingIterator(Iterator):

    def __init__(self, key_domain, value_domain):
        key_iterator = key_domain.iterator
        value_iterator = value_domain.iterator
        itype = Map(key_domain.type, value_iterator.itype)
        element_type = Map(key_domain.type,
                           value_domain.type)
        super().__init__(itype, element_type)

        env = {
            "key_itype" : key_iterator.itype,
            "key_reset" : key_iterator.reset_fn,
            "key_is_valid" : key_iterator.is_valid_fn,
            "key_next" : key_iterator.next_fn,
            "key_value" : key_iterator.value_fn,
            "value_reset" : value_iterator.reset_fn,
            "value_itype" : value_iterator.itype,
            "type" : element_type,
            "value_is_valid" : value_iterator.is_valid_fn,
            "value_value" : value_iterator.value_fn,
            "value_next" : value_iterator.next_fn,
        }

        self.reset_fn.code("""
            {{key_itype}} key_iterator;
            {{key_reset}}(key_iterator);
            {{value_itype}} value_iterator;
            {{value_reset}}(value_iterator);
            while ({{key_is_valid}}(key_iterator)) {
                iter[{{key_value}}(key_iterator)] = value_iterator;
                {{key_next}}(key_iterator);
            }
        """, **env)

        self.next_fn.code("""
            if (iter.begin() == iter.end()) {
                return;
            }
            auto last = --iter.end();
            for (auto i = iter.begin(); i != last; i++) {
                {{value_next}}(i->second);
                if ({{value_is_valid}}(i->second)) {
                    return;
                }
                {{value_reset}}(i->second);
            }
            {{value_next}}(iter.rbegin()->second);
        """, **env)

        self.is_valid_fn.code("""
            if (iter.begin() != iter.end()) {
                return {{value_is_valid}}(iter.rbegin()->second);
            } else {
                return false;
            }
        """, **env)

        self.value_fn.code("""
            {{type}} result;
            for (auto const &i : iter) {
                result[i.first] = {{value_value}}(i.second);
            }
            return result;
        """, **env)


class MappingIterator2(Iterator):

    def __init__(self, key_domain, value_domains, choose_fn):
        key_iterator = key_domain.iterator
        iterators = tuple(d.iterator for d in value_domains)
        union = Union(i.itype for i in iterators)
        itype = Map(key_domain.type, union)
        element_type = Map(key_domain.type,
                           value_domains[0].type)
        super().__init__(itype, element_type)

        env = {
            "key_itype" : key_iterator.itype,
            "key_type" : key_iterator.element_type,
            "key_reset" : key_iterator.reset_fn,
            "key_is_valid" : key_iterator.is_valid_fn,
            "key_next" : key_iterator.next_fn,
            "key_value" : key_iterator.value_fn,
            "type" : element_type,
            "itype" : itype,
            "union" : union,
            "choose_fn" : choose_fn,
            "_iterators" : iterators
        }

        uses = tuple(i.reset_fn for i in iterators) + \
               tuple(i.next_fn for i in iterators) + \
               tuple(i.is_valid_fn for i in iterators) + \
               tuple(i.value_fn for i in iterators)


        self.reset_fn.code("""
            {{key_itype}} key_iterator;
            {{key_reset}}(key_iterator);
            {%- for i in _iterators %}
                {{b(i.itype)}} i{{loop.index0}};
                {{b(i.reset_fn)}}(i{{loop.index0}});
            {%- endfor %}
            while ({{key_is_valid}}(key_iterator)) {
                {{key_type}} key = {{key_value}}(key_iterator);
                switch({{choose_fn}}(key)) {
                {%- for i in _iterators %}
                case {{loop.index0}}:
                    iter[key] = {{union}}({{loop.index0}}, i{{loop.index0}});
                    break;
                {%- endfor %}
                default:
                    assert(0);
                }
                {{key_next}}(key_iterator);
            }
        """, **env).uses(uses)

        self.next_fn.code("""
            if (iter.begin() == iter.end()) {
                return;
            }
            auto last = --iter.end();
            for (auto i = iter.begin(); i != last; i++) {
                switch(i->second.tag()) {
                {%- for i in _iterators %}
                case {{loop.index0}}:
                    {{b(i.next_fn)}}(i->second.get{{loop.index0}}());
                    if ({{b(i.is_valid_fn)}}(i->second.get{{loop.index0}}())) {
                        return;
                    }
                    {{b(i.reset_fn)}}(i->second.get{{loop.index0}}());
                    break;
                {%- endfor %}
                default:
                    assert(0);
                }

            }

            switch(iter.rbegin()->second.tag()) {
            {%- for i in _iterators %}
            case {{loop.index0}}:
                {{b(i.next_fn)}}(iter.rbegin()->second.get{{loop.index0}}());
                return;
            {%- endfor %}
            default:
                assert(0);
            }
        """, **env).uses(uses)

        self.is_valid_fn.code("""
            if (iter.begin() != iter.end()) {
                switch(iter.rbegin()->second.tag()) {
                {%- for i in _iterators %}
                case {{loop.index0}}:
                    return {{b(i.is_valid_fn)}}(iter.rbegin()->second.get{{loop.index0}}());
                {%- endfor %}
                default:
                    assert(0);
                }
            } else {
                return false;
            }
        """, **env).uses(uses)

        self.value_fn.code("""
            {{type}} result;
            for (auto const &i : iter) {
                switch(i.second.tag()) {
                {%- for i in _iterators %}
                case {{loop.index0}}:
                    result[i.first] = {{b(i.value_fn)}}(i.second.get{{loop.index0}}());
                    continue;
                {%- endfor %}
                default:
                    assert(0);
                }
            }
            return result;
        """, **env).uses(uses)
