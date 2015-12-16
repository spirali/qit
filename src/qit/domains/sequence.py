from qit.base.int import Int
from qit.base.bool import Bool
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
        itype = Bool() * Vector(iterator.itype)
        element_type = Vector(iterator.element_type)

        super().__init__(itype, element_type)

        self.reset_fn.code("""
            {{inner_itype}} item;
            {{reset_fn}}(item);
            iter.v1 = {{ivector}}({{size}}, item);
            iter.v0 = std::all_of(iter.v1.begin(), iter.v1.end(), {{is_valid_fn}});
        """, ivector=itype.types[1],
             size=size,
             inner_itype=iterator.itype,
             is_valid_fn=iterator.is_valid_fn,
             reset_fn=iterator.reset_fn)

        self.next_fn.code("""
            size_t size = iter.v1.size();
            if (size == 0) {
                iter.v0 = false;
                return;
            }
            size_t i;
            for(i = 0; i < size - 1; i++) {
                {{next_fn}}(iter.v1[i]);
                if ({{is_valid_fn}}(iter.v1[i])) {
                    return;
                } else {
                    {{reset_fn}}(iter.v1[i]);
                }
            }
            {{next_fn}}(iter.v1[i]);
            iter.v0 = {{is_valid_fn}}(iter.v1[i]);
        """, next_fn=iterator.next_fn,
        is_valid_fn=iterator.is_valid_fn, reset_fn=iterator.reset_fn)

        self.is_valid_fn.code("return iter.v0;")

        self.value_fn.code("""
            {{type}} result;
            size_t size = iter.v1.size();
            result.reserve(size);
            for(size_t i = 0; i < size; i++) {
                result.push_back({{value_fn}}(iter.v1[i]));
            }
            return result;
        """, type=element_type, value_fn=iterator.value_fn)
