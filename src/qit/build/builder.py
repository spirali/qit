
#import writer as writer

from qit.build.writer import CppWriter

class CppBuilder(object):

    def __init__(self):
        self.writer = CppWriter()
        self.id_counter = 100

    def build_print_all(self, collection):
        self.write_header()
        self.write_declaretions(collection)
        self.main_begin()
        iterator = self.make_iterator(collection)
        element = self.make_element(collection)
        self.writer.line("while ({}.next({}))", iterator, element)
        self.writer.block_begin()
        self.writer.line("std::cout << {} << std::endl;", element)
        self.writer.block_end()
        self.main_end()
        print(self.writer.get_string())

    def write_declaretions(self, collection):
        collections = collection.get_all_subcollections()
        for c in collections:
            c.declare(self)

    def write_header(self):
        self.writer.line("/*")
        self.writer.line("       QIT generated file")
        self.writer.line("*/")
        self.writer.emptyline()
        self.writer.line("#include <iostream>")
        self.writer.line("#include <qit.h>")
        self.writer.line("#include <stdlib.h>")
        self.writer.line("#include <time.h>")
        self.writer.emptyline()

    def main_begin(self):
        self.writer.line("int main()")
        self.writer.block_begin()
        self.writer.line("srand(time(NULL));")

    def main_end(self):
        self.writer.line("return 0;")
        self.writer.block_end();

    def new_id(self, prefix="v"):
        self.id_counter += 1
        return "{}{}".format(prefix, self.id_counter)

    def make_generator(self, collection):
        variables = []
        for parent in collection.parent_collections:
            variables.append(self.make_generator(parent))
        for parent in collection.parent_generators:
            variables.append(self.make_generator(parent))
        args = tuple(variables) + collection.get_constructor_args(self)
        variable = self.new_id("g")
        self.writer.line("{} {}({});",
                         collection.get_rgenerator_type(self),
                         variable,
                         ",".join(args))
        return variable

    def make_iterator(self, collection):
        variables = []
        for parent in collection.parent_collections:
            variables.append(self.make_iterator(parent))
        for parent in collection.parent_generators:
            variables.append(self.make_generator(parent))
        args = tuple(variables) + collection.get_constructor_args(self)
        variable = self.new_id("i")
        self.writer.line("{} {}({});",
                         collection.get_iterator_type(self),
                         variable,
                         ",".join(args))
        return variable

    def make_element(self, collection):
        variable = self.new_id()
        self.writer.line("{} {};",
                         self.get_element_type(collection),
                         variable)
        return variable

    def get_element_type(self, collection):
        iterator_type = collection.get_iterator_type(self)
        return "{}::value_type".format(iterator_type)

    ## Method for multiple dispatch of base classes

    def get_generator_iterator(self, transformation):
        return "qit::GeneratorIterator<{} >" \
                .format(transformation.collection.get_rgenerator_type(self))

    # Range

    def get_range_iterator(self):
        return "qit::RangeIterator"

    def get_range_rgenerator(self):
        return "qit::RangeGenerator"

    def get_range_constructor_args(self, range):
        return (str(range.stop),)

    # Take

    def get_take_iterator(self, take):
        return "qit::TakeIterator<{} >" \
                .format(take.collection.get_iterator_type(self))

    def get_take_constructor_args(self, take):
        return (str(take.count),)

    # Product

    def get_product_iterator(self, product):
        return product.name + "Iterator"

    def get_product_rgenerator(self, product):
        return product.name + "Generator"

    def declare_product(self, product):
        self.declare_product_class(product)
        self.declare_product_iterator(product)
        self.declare_product_generator(product)

    def declare_product_class(self, product):
        self.writer.class_begin(product.name)
        self.writer.line("public:")

        ## Constructor
        for name, collection in product.items:
            self.writer.line("{} {};",
                             self.get_element_type(collection),
                             name)
        self.writer.class_end()

        ## Stream
        self.writer.line("std::ostream& operator<<(std::ostream& os, const {}& v)",
                  product.name)
        self.writer.block_begin()
        self.writer.line("os << \"{{\";")
        for i, name in enumerate(product.names):
            if i != 0:
                self.writer.line("os << \",\";")
            self.writer.line("os << v.{};", name)
        self.writer.line("return os << \"}}\";")
        self.writer.block_end()

    def declare_product_iterator(self, product):
        iterator_name = product.get_iterator_type(self)
        self.writer.class_begin(iterator_name)
        self.writer.line("public:")
        self.writer.line("typedef {} value_type;", product.name)

        # Attributes
        for name, collection in product.items:
            self.writer.line("{} {};",
                             collection.get_iterator_type(self),
                             name)
        self.writer.line("bool _inited;")

        # Contructor
        args = [ "{} &{}".format(c.get_iterator_type(self), name)
                 for name, c in product.items ]
        constructors = [ "{0}({0})".format(name) for name in product.names ]
        constructors.append("_inited(false)")
        self.writer.line("{}({}) {} {}",
                         iterator_name,
                         ",".join(args),
                         ":" if constructors else "",
                         ",".join(constructors))
        self.writer.block_begin()
        self.writer.block_end()

        # Next
        self.writer.line("bool next({} &v)", product.name)
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
            self.writer.line("{}.reset();", name)
        self.writer.block_end()

        self.writer.class_end()


    def declare_product_generator(self, product):
        generator_name = product.get_rgenerator_type(self)
        self.writer.class_begin(generator_name)
        self.writer.line("public:")
        self.writer.line("typedef {} value_type;", product.name)

        # Attributes
        for name, collection in product.items:
            self.writer.line("{} {};",
                             collection.get_rgenerator_type(self),
                             name)

        # Contructor
        args = [ "{} &{}".format(c.get_rgenerator_type(self), name)
                 for name, c in product.items ]
        constructors = [ "{0}({0})".format(name) for name in product.names ]
        self.writer.line("{}({}) {} {}",
                         generator_name,
                         ",".join(args),
                         ":" if constructors else "",
                         ",".join(constructors))
        self.writer.block_begin()
        self.writer.block_end()

        # Next
        self.writer.line("void generate({} &v)", product.name)
        self.writer.block_begin()
        for name in product.names:
            self.writer.line("{0}.generate(v.{0});", name)
        self.writer.block_end()

        # Reset
        self.writer.line("void reset()")
        self.writer.block_begin()
        self.writer.block_end()

        self.writer.class_end()
