from qit.base.int import Int
from qit.base.vector import Vector
from qit.domains.domain import Domain
from qit.domains.iterator import Iterator
from qit.base.function import Function
from qit.functions.int import power

class Sequence(Domain):

    def __init__(self, domain, size):
        vector = Vector(domain.type)
        size = Int().value(size)

        if domain.iterator is not None:
            iterator = SequenceIterator(domain.iterator, size)
        else:
            iterator = None

        if domain.generator is not None:
            generator = Function().returns(vector).code("""
                {{type}} result;
                size_t size = {{size}};
                result.reserve(size);
                for(size_t i = 0; i < size; i++) {
                    result.push_back({{generator}});
                }
                return result;
            """, generator=domain.generator, size=size, type=vector)()
        else:
            generator = None

        if domain.size is not None:
            size = Int().value(size)
            domain_size = power(domain.size, size)
        else:
            domain_size = None

        super().__init__(vector, iterator, generator, domain_size)


class SequenceIterator(Iterator):

    def __init__(self, iterator, size):
        size = Int().value(size)
        itype = Vector(iterator.itype)
        element_type = Vector(iterator.element_type)

        init_expr = Function().returns(itype).code("""
            return {{itype}}({{size}}, {{init_expr}});
        """, itype=itype, size=size, init_expr=iterator.init_expr)()

        super().__init__(itype, element_type, init_expr)

        self.next_fn.code("""
            size_t size = iter.size();
            size_t i;
            for(i = 0; i < size - 1; i++) {
                {{next_fn}}(iter[i]);
                if ({{is_valid_fn}}(iter[i])) {
                    return;
                } else {
                    iter[i] = {{init_expr}};
                }
            }
            {{next_fn}}(iter[i]);
        """, next_fn=iterator.next_fn,
        is_valid_fn=iterator.is_valid_fn, init_expr=iterator.init_expr)

        self.is_valid_fn.code("""
            if (iter.begin() == iter.end()) {
                return false;
            }
            return std::all_of(iter.begin(), iter.end(), {{is_valid_fn}});
        """, is_valid_fn=iterator.is_valid_fn)

        self.value_fn.code("""
            {{type}} result;
            size_t size = iter.size();
            result.reserve(size);
            for(size_t i = 0; i < size; i++) {
                result.push_back({{value_fn}}(iter[i]));
            }
            return result;
        """, type=element_type, value_fn=iterator.value_fn)
