
#import writer as writer

from qit.build.writer import CppWriter


class CppBuilder(object):

    def __init__(self):
        self.writer = CppWriter()
        self.id_counter = 100
        self.declaration_keys = []
        self.autonames = []

    def get_autoname(self, key, prefix):
        for k, name in self.autonames:
            if key == k:
                return name
        name = self.new_id(prefix)
        self.autonames.append((key, name))
        return name

    def build_print_all(self, iterator):
        self.write_header()
        iterator.declare(self)
        self.main_begin()
        variable = iterator.make_iterator(self)
        element = self.make_element(iterator.output_type.basic_type)
        self.writer.line("while ({}.next({}))", variable, element)
        self.writer.block_begin()
        self.writer.line("std::cout << {} << std::endl;", element)
        self.writer.block_end()
        self.main_end()

    def build_collect(self, iterator):
        self.write_header()
        iterator.declare(self)
        self.main_begin()
        variable = iterator.make_iterator(self)
        element = self.make_element(iterator.output_type.basic_type)
        self.init_fifo()
        self.writer.line("while ({}.next({}))", variable, element)
        self.writer.block_begin()
        self.writer.line("qit::write(output, {});", element)
        self.writer.block_end()
        self.main_end()

    def init_fifo(self):
        self.writer.line("assert(argc > 1);")
        self.writer.line("FILE *output = fopen(argv[1], \"w\");")

    def write_header(self):
        self.writer.line("/*")
        self.writer.line("       QIT generated file")
        self.writer.line("*/")
        self.writer.emptyline()
        self.writer.line("#include <assert.h>")
        self.writer.line("#include <iostream>")
        self.writer.line("#include <qit.h>")
        self.writer.line("#include <stdlib.h>")
        self.writer.line("#include <time.h>")
        self.writer.emptyline()

    def main_begin(self):
        self.writer.line("int main(int argc, char **argv)")
        self.writer.block_begin()
        self.writer.line("srand(time(NULL));")

    def main_end(self):
        self.writer.line("return 0;")
        self.writer.block_end();

    def new_id(self, prefix="v"):
        self.id_counter += 1
        return "{}{}".format(prefix, self.id_counter)

    def make_element(self, basic_type):
        variable = self.new_id()
        self.writer.line("{} {};",
                         basic_type.get_element_type(self),
                         variable)
        return variable

    ## Method for multiple dispatch of base classes

    def get_generator_iterator(self, transformation):
        return "qit::GeneratorIterator<{} >" \
                .format(transformation.generator.get_generator_type(self))

    def make_basic_iterator(self, iterator, iterators=(), args=()):
        return self.make_iterator(iterator,
                                  tuple(c.make_iterator(self)
                                     for c in iterators) + args)

    def make_iterator(self, iterator, args):
        variable = self.new_id("i")
        self.writer.line("{} {}({});",
                         iterator.get_iterator_type(self),
                         variable,
                         ",".join(args))
        return variable

    def make_basic_generator(self, iterator, iterators=(), args=()):
        return self.make_generator(iterator,
                                  tuple(c.make_generator(self)
                                     for c in iterators) + args)

    def make_generator(self, iterator, args):
        variable = self.new_id("g");
        self.writer.line("{} {}({});",
                         iterator.get_generator_type(self),
                         variable,
                         ",".join(args))
        return variable


    def check_declaration_key(self, key):
        if key in self.declaration_keys:
            return True
        self.declaration_keys.append(key)
        self.writer.line("/* Declaration: {} */", key)
        return False

    # Int

    def get_int_type(self):
        return "int"

    # Range

    def get_range_iterator(self):
        return "qit::RangeIterator"

    def get_range_generator(self):
        return "qit::RangeGenerator"

    # Take

    def get_take_iterator(self, take):
        return "qit::TakeIterator<{} >" \
                .format(take.parent_iterator.get_iterator_type(self))

    # Map

    def get_map_iterator(self, map):
        return "qit::MapIterator<{}, {}, {} >" \
                .format(map.parent_iterator.get_iterator_type(self),
                        map.function.return_type.get_element_type(self),
                        map.function.name)


    # Product

    def get_product_type(self, product):
        if product.name is None:
            return self.get_autoname(product, "Product")
        else:
            return product.name

    def get_product_iterator(self, iterator):
        type_name = self.get_product_type(iterator.output_type)
        return self.get_autoname(iterator, type_name + "Iterator")

    def get_product_generator(self, generator):
        type_name = self.get_product_type(generator.output_type)
        return self.get_autoname(generator, type_name + "Generator")

    def declare_product_class(self, product):
        if self.check_declaration_key((product, "class")):
            return
        product_type = self.get_product_type(product)
        self.writer.class_begin(product_type)
        self.writer.line("public:")

        ## Constructor
        for name, t in product.items:
            self.writer.line("{} {};",
                             t.basic_type.get_element_type(self),
                             name)

        # Write
        self.writer.line("void write(FILE *f)")
        self.writer.block_begin()
        for name in product.names:
            self.writer.line("qit::write(f, {});", name)
        self.writer.block_end()

        self.writer.class_end()

        ## Stream
        self.writer.line("std::ostream& operator<<(std::ostream& os, const {}& v)",
                  product_type)
        self.writer.block_begin()
        self.writer.line("os << \"{{\";")
        for i, name in enumerate(product.names):
            if i != 0:
                self.writer.line("os << \",\";")
            self.writer.line("os << v.{};", name)
        self.writer.line("return os << \"}}\";")
        self.writer.block_end()


    def declare_product_iterator(self, iterator):
        if self.check_declaration_key((iterator, "iterator")):
            return

        product = iterator.output_type
        iterator_type = iterator.get_iterator_type(self)
        element_type = product.get_element_type(self)

        self.writer.class_begin(iterator_type)
        self.writer.line("public:")
        self.writer.line("typedef {} value_type;", element_type)

        names_iterators = list(zip(product.names, iterator.iterators))

        # Attributes
        for name, i in names_iterators:
            self.writer.line("{} &{};",
                             i.get_iterator_type(self),
                             name)
        self.writer.line("bool _inited;")

        # Contructor
        args = [ "{} &{}".format(i.get_iterator_type(self), name)
                 for name, i in names_iterators ]
        constructors = [ "{0}({0})".format(name) for name in product.names ]
        constructors.append("_inited(false)")
        self.writer.line("{}({}) {} {}",
                         iterator_type,
                         ",".join(args),
                         ":" if constructors else "",
                         ",".join(constructors))
        self.writer.block_begin()
        self.writer.block_end()

        # Next
        self.writer.line("bool next({} &v)", element_type)
        self.writer.block_begin()
        self.writer.if_begin("_inited")
        for i, name in enumerate(product.names):
            self.writer.if_begin("{0}.next(v.{0})", name)
            self.writer.line("return true;")
            self.writer.block_end()
            if i != len(product.items) - 1:
                self.writer.line("{}.reset();", name)
                self.writer.line("{0}.next(v.{0});", name)
        self.writer.line("return false;")
        self.writer.else_begin()
        for name in product.names:
            self.writer.if_begin("!{0}.next(v.{0})", name)
            self.writer.line("return false;")
            self.writer.block_end()
        self.writer.line("_inited = true;")
        self.writer.line("return true;")
        self.writer.block_end()
        self.writer.block_end()

        # Reset
        self.writer.line("void reset()")
        self.writer.block_begin()
        for name in product.names:
            self.writer.line("_inited = false;")
            self.writer.line("{}.reset();", name)

        self.writer.block_end()

        self.writer.class_end()


    def declare_product_generator(self, generator):
        if self.check_declaration_key((generator, "generator")):
            return

        product = generator.output_type
        generator_type = generator.get_generator_type(self)
        element_type = product.get_element_type(self)
        self.writer.class_begin(generator_type)
        self.writer.line("public:")
        self.writer.line("typedef {} value_type;", element_type)

        # Attributes
        names_generators = list(zip(product.names, generator.generators))
        for name, generator in names_generators:
            self.writer.line("{} &{};",
                             generator.get_generator_type(self),
                             name)

        # Contructor
        args = [ "{} &{}".format(generator.get_generator_type(self), name)
                 for name, generator in names_generators ]
        constructors = [ "{0}({0})".format(name) for name in product.names ]
        self.writer.line("{}({}) {} {}",
                         generator_type,
                         ",".join(args),
                         ":" if constructors else "",
                         ",".join(constructors))
        self.writer.block_begin()
        self.writer.block_end()

        # Next
        self.writer.line("void generate({} &v)", element_type)
        self.writer.block_begin()
        for name in product.names:
            self.writer.line("{0}.generate(v.{0});", name)
        self.writer.block_end()

        self.writer.class_end()

    # Function

    def declare_function(self, function):
        self.writer.class_begin(function.name)
        self.writer.line("public:")
        params = [ "const {} &{}".format(c.get_element_type(self), name)
                   for c, name in function.params ]
        self.writer.line("{} operator()({})",
                         function.return_type.get_element_type(self),
                         ",".join(params))
        self.writer.block_begin()
        self.writer.text(function.inline_code)
        self.writer.block_end()

        self.writer.class_end()

