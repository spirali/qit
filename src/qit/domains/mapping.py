from qit.base.map import Map
from qit.domains.domain import Domain
from qit.domains.iterator import Iterator


class Mapping(Domain):

    def __init__(self, key_domain, value_domain):
        map_type = Map(key_domain.type, value_domain.type)
        iterator = MappingIterator(key_domain, value_domain)
        super().__init__(map_type, iterator)


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
