
from qit.base.bool import Bool
from qit.base.struct import Struct
from qit.domains.domain import Domain
from qit.domains.iterator import Iterator
from qit.base.function import Function
from qit.functions.int import multiplication_n

class Product(Domain):

    def __init__(self, *args):

        domains = []
        struct_args = []

        for arg in args:
            if isinstance(arg, tuple) and len(arg) == 2:
                domain = arg[0].make_domain()
                domains.append(domain)
                struct_args.append((domain.type, arg[1]))
            else:
                domains.append(arg.make_domain())
                struct_args.append(arg.type)
        type = Struct(*struct_args)
        super().__init__(
                type,
                self._make_iterator(type, domains),
                self._make_generator(type, domains),
                self._make_size(domains),
                self._make_indexer(domains))
        self.domains = tuple(domains)

    def _make_iterator(self, type, domains):
        iterators = [ d.iterator for d in domains ]
        if all(iterators):
            return ProductIterator(type, iterators)

    def _make_generator(self, type, domains):
        generators = tuple(d.generator for d in domains)
        if all(generators):
            generator = Function().returns(type).code("""
            return {
            {% for g in _generators %}
               {{b(g)}}{% if not loop.last %},{% endif %}
            {% endfor %}
            };
            """, _generators=generators).uses(generators)
            return generator()

    def _make_size(self, domains):
        sizes = [ d.size for d in domains ]
        if all(sizes):
            return multiplication_n(len(sizes))(*sizes)

    def _make_indexer(self, domains):
        indexers = [ d.indexer for d in domains ]
        if all(indexers):
            """
            indexer = FunctionWithExprs(start=start, step=step).returns(Int())
            indexer.takes(Int(), "_v")
            indexer.code("return (_v - {start}) / {step};")
            """

    def __mul__(self, other):
        args = list(zip(self.domains, self.type.names))
        args.append(other)
        return Product(*args)


class ProductIterator(Iterator):

    def __init__(self, struct, iterators):
        items = [ (Bool(), "_is_valid") ]
        items += [ (i.itype, name)
                   for i, name in zip(iterators, struct.names) ]
        itype = Struct(*items)
        iters = tuple(zip(struct.names, iterators))

        objects = set()
        for i in iterators:
            objects.update(i.childs)
        objects = tuple(objects)

        init_expr = Function(returns=itype).code("""
            {{itype}} iter(
                true
            {% for name, i in _iters %}
                ,{{b(i.init_expr)}}
            {% endfor %}
            );
            {% for name, i in _iters %}
                if (!({{b(i.is_valid_fn)}}(iter.{{name}}))) {
                    iter._is_valid = false;
                    return iter;
                }
            {% endfor %}
            return iter;

        """, itype=itype, _iters=iters, struct=struct).uses(objects)()

        super().__init__(itype, struct, init_expr)

        self.next_fn.code("""
            {% for name, i in _iters %}
                {{ b(i.next_fn) }}(iter.{{name}});
                if ({{ b(i.is_valid_fn) }}(iter.{{name}})) {
                    return;
                } else {
                    iter.{{name}} = {{b(i.init_expr)}};
                }
            {% endfor %}
            iter._is_valid = false;
        """, _iters=iters).uses(objects)

        self.is_valid_fn.code("""
            return iter._is_valid;
        """, _iters=iters).uses(objects)

        self.value_fn.code("""
            return {
            {% for name, i in _iters %}
                {{b(i.value_fn)}}(iter.{{name}})
                {% if not loop.last %},{% endif %}
            {% endfor %}
            };
        """, _iters=iters, struct=struct).uses(objects)
