from qit.base.map import Map
from qit.base.function import Function
from qit.domains.domain import Domain
from qit.domains.iterator import Iterator


class Mapping(Domain):

    def __init__(self, key_domain, value_domain, choose_fn=None):
        assert not isinstance(value_domain, tuple) or choose_fn is not None

        map_type = Map(key_domain.type, value_domain.type)

        if key_domain.is_iterable() and value_domain.is_iterable():
            iterator = MappingIterator(key_domain, value_domain)
        else:
            iterator = None

        if key_domain.is_iterable() and value_domain.is_generable():
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
        else:
            generator = None

        super().__init__(map_type, iterator, generator)


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
