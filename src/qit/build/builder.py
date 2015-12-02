
#import writer as writer

from qit.base.system import RuleType
from qit.build.writer import CppWriter
from qit.base.utils import sorted_variables

class CppBuilder(object):

    def __init__(self, env):
        self.env = env
        self.writer = CppWriter()
        self.id_counter = 100
        self.declaration_keys = []
        self.autonames = {}
        self.included_filenames = set()

    def get_autoname(self, obj):
        name = self.autonames.get(obj)
        if name is not None:
            return name
        name = self.new_id(obj.autoname_prefix)
        self.autonames[obj] = name
        return name

    def include_filename(self, filename):
        if filename in self.included_filenames:
            return
        self.included_filenames.add(filename)
        self.writer.line("#include \"{}\"", filename)

    def build_collect(self, obj, args):
        self.write_header()
        obj.declare_all(self)
        self.main_begin()
        self.init_fifo()
        self.init_variables(args)
        variable = obj.write_into_variable(self)
        self.writer.line("qit::write(output, {});", variable)
        self.writer.line("fclose(output);")
        self.main_end()

    def write_expression_into_variable(self, expr):
        variable = self.new_id()
        self.writer.line("{} {} = {};",
                         expr.type.build_type(self),
                         variable,
                         expr.build_value(self))
        return variable

    def build_object(self, type, args):
        args = ",".join(a.build_value(self) for a in args)
        return "{}({})".format(type.build_type(self), args)

    def write_iterator_write_method(self):
        self.writer.line("QIT_ITERATOR_WRITE_METHOD")

    def make_sequence_from_iterator(self, iterator):
        result_variable = self.new_id("result")
        self.writer.line("{} {};",
                         iterator.output_type.build_type(self),
                         result_variable)
        iterator_variable = iterator.make_iterator(self)
        element = self.make_element(iterator.output_type.basic_type)
        self.writer.line("while ({}.next({}))", iterator_variable, element)
        self.writer.block_begin()
        self.writer.line("{}.push_back({});", result_variable, element)
        self.writer.block_end()
        return result_variable

    def make_element_from_iterator(self, iterator):
        iterator_variable = iterator.make_iterator(self)
        element = self.make_element(iterator.output_type.basic_type)
        self.writer.line("assert({}.next({}));", iterator_variable, element)
        return element

    def init_fifo(self):
        self.writer.line("assert(argc > 1);")
        self.writer.line("FILE *output = fopen(argv[1], \"w\");")

    def init_variables(self, args):
        for variable, value in sorted(args.items(), key=lambda v: v[0].name):
            self.writer.line("{} {}({});",
                             variable.type.build_type(self),
                             variable.name,
                             value.build_value(self))

    def write_header(self):
        self.writer.line("/*")
        self.writer.line("       QIT generated file")
        self.writer.line("*/")
        self.writer.emptyline()
        self.writer.line("#include <qit.h>")
        self.writer.emptyline()
        self.writer.line("#include <vector>")
        self.writer.line("#include <set>")
        self.writer.line("#include <iostream>")
        self.writer.line("#include <assert.h>")
        self.writer.line("#include <stdlib.h>")
        self.writer.line("#include <time.h>")

        self.writer.emptyline()
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

    """
    def declare_type_alias(self, type):
        if self.check_declaration_key(type):
            return
        if type.name is not None:
            self.writer.line("typedef {} {};",
                             type.basic_type.get_element_type(self),
                             type.name)
    """

    ## Method for multiple dispatch of base classes

    def declare_generator_iterator(self, iterator):
        if self.check_declaration_key(iterator):
            return
        expression = iterator.generator
        name = iterator.build_type(self)
        element_type = expression.type.build_type(self)
        self.writer.class_begin(name)
        self.writer.line("public:")
        self.writer.line("typedef {} value_type;", element_type)

        variables = sorted_variables(iterator.get_variables())

        # Args
        for v in variables:
            self.writer.line("const {} &{};",
                             v.type.build_type(self),
                             v.build_value(self))

        #Constructor
        if variables:
            args = ",".join(
                "const {} &{}".format(v.type.build_type(self),
                                      v.build_value(self))
                for v in variables)
            inits = ",".join("{0}({0})".format(v.build_value(self))
                for v in variables)
            self.writer.line("{}({}) : {} {{}}", name, args, inits)

        # Next
        self.writer.line("bool next({} &out)", element_type)
        self.writer.block_begin()
        self.writer.line("out = {};", expression.build_value(self))
        self.writer.line("return true;")
        self.writer.block_end()

        # Reset
        self.writer.line("void reset()")
        self.writer.block_begin()
        self.writer.line("// Do nothing")
        self.writer.block_end()

        # Write
        self.write_iterator_write_method()
        self.writer.class_end()

    def make_basic_iterator(self, iterator, iterators=(), args=()):
        return self.make_iterator(iterator,
                                  tuple(c.make_iterator(self)
                                     for c in iterators) + args)

    def make_instance(self, type, prefix, args=()):
        variable = self.new_id(prefix)
        if args:
            self.writer.line("{} {}({});", type, variable, ",".join(args))
        else:
            self.writer.line("{} {};", type, variable)
        return variable

    def check_declaration_key(self, key):
        if key in self.declaration_keys:
            return True
        self.declaration_keys.append(key)
        self.writer.line("/* Declaration: {} */", key)
        return False

    # Int

    def build_int_type(self):
        return "int"

    def build_int_constant(self, value):
        assert isinstance(value, int)
        return str(value)

    # Bool

    def build_bool_type(self):
        return "bool"

    def build_bool_constant(self, value):
        assert isinstance(value, bool)
        return "true" if value else "false"

    # Range

    def build_range_iterator(self):
        return "qit::RangeIterator"

    # Take

    def build_take_iterator(self, take):
        return "qit::TakeIterator<{} >" \
                .format(take.parent_iterator.type.build_type(self))

    # Sort

    def build_sort_iterator(self, sort):
        return "qit::SortIterator<{} >" \
                .format(sort.parent_iterator.type.build_type(self))

    # Map

    def build_map_iterator(self, map):
        return "qit::MapIterator<{}, {}, {} >" \
                .format(map.parent_iterator.type.build_type(self),
                        map.function.return_type.build_type(self),
                        self.get_autoname(map.function))

    # Filter

    def build_filter_iterator(self, filter):
        return "qit::FilterIterator<{}, {} >" \
                .format(filter.parent_iterator.type.build_type(self),
                        self.get_autoname(filter.function))

    # Struct

    def build_struct_type(self, struct):
        return self.get_autoname(struct)

    def declare_struct(self, struct):
        if self.check_declaration_key(struct):
            return
        struct_type = self.build_struct_type(struct)
        self.writer.class_begin(struct_type)
        self.writer.line("public:")

        ## Attributes
        for name, t in zip(struct.names, struct.types):
            self.writer.line("{} {};",
                             t.build_type(self),
                             name)

        args = ",".join("const {} &{}".format(t.build_type(self), name)
                        for t, name in zip(struct.types, struct.names))

        consts = ",".join("{0}({0})".format(name)
                        for name in struct.names)

        self.writer.line("{}({}) : {} {{}}", struct_type, args, consts)
        self.writer.line("{}() {{}}", struct_type)

        # Write
        self.writer.line("void write(FILE *f) const")
        self.writer.block_begin()
        for name in struct.names:
            self.writer.line("qit::write(f, {});", name)
        self.writer.block_end()

        # Operator <
        self.writer.line("bool operator <(const {} &other) const", struct_type)
        self.writer.block_begin()
        for name in struct.names:
            self.writer.if_begin("{0} < other.{0}", name)
            self.writer.line("return true;")
            self.writer.block_end()
            self.writer.if_begin("{0} == other.{0}", name)
        for name in struct.names:
            self.writer.block_end()
        self.writer.line("return false;")
        self.writer.block_end()

        # Operator ==
        self.writer.line("bool operator ==(const {} &other) const", struct_type)
        self.writer.block_begin()
        self.writer.line("return {};",
                         " && ".join("({0} == other.{0})".format(name)
                             for name in struct.names))
        self.writer.block_end()
        self.writer.class_end()

    def build_struct_constant(self, struct, value):
        assert len(value) == len(struct.names)
        args = ",".join(t.build_constant(self, v)
                        for t, v in zip(struct.types, value))
        return "{}({})".format(self.build_struct_type(struct), args)

    # Vector

    def build_vector_type(self, sequence):
        return "std::vector<{} >".format(
            sequence.element_type.build_type(self))

    def build_vector_constant(self, sequence, value):
        t = sequence.element_type
        args = ",".join(t.build_constant(self, v) for v in value)
        return "{{ {} }}".format(args)

    # Product

    def declare_product_iterator(self, iterator):
        if self.check_declaration_key(iterator):
            return

        struct = iterator.output_type
        iterator_type = iterator.build_type(self)
        element_type = struct.build_type(self)

        self.writer.class_begin(iterator_type)
        self.writer.line("public:")
        self.writer.line("typedef {} value_type;", element_type)

        names_iterators = list(zip(struct.names, iterator.iterators))

        # Attributes
        for name, i in names_iterators:
            self.writer.line("{} {};",
                             i.type.build_type(self),
                             name)
        self.writer.line("bool _inited;")

        # Contructor
        args = [ "const {} &{}".format(i.type.build_type(self), name)
                 for name, i in names_iterators ]
        constructors = [ "{0}({0})".format(name) for name in struct.names ]
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
        for i, name in enumerate(struct.names):
            self.writer.if_begin("{0}.next(v.{0})", name)
            self.writer.line("return true;")
            self.writer.block_end()
            if i != len(struct.names) - 1:
                self.writer.line("{}.reset();", name)
                self.writer.line("{0}.next(v.{0});", name)
        self.writer.line("return false;")
        self.writer.else_begin()
        for name in struct.names:
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
        self.writer.line("_inited = false;")
        for name in struct.names:
            self.writer.line("{}.reset();", name)
        self.writer.block_end()

        # Write
        self.write_iterator_write_method()

        self.writer.class_end()

    def write_struct_generator(self, struct, generators):
        assert len(struct.names) == len(generators)
        self.writer.line("{} s;", struct.build_type(self))
        for name, generator in zip(struct.names, generators):
            self.writer.line("s.{} = {};", name, generator.build_value(self))
        self.writer.line("return s;")

    # Sequences

    def build_sequence_iterator(self, iterator):
        return "qit::SequenceIterator<{} >".format(
            iterator.element_iterator.type.build_type(self))

    def write_sequence_generator(self, generator):
        self.writer.line("{} v;", generator.return_type.build_type(self))
        self.writer.line("size_t size = {};", generator.size.build_value(self))
        self.writer.line("v.reserve(size);")
        self.writer.line("for (int i = 0; i < size; i++)")
        self.writer.block_begin()
        self.writer.line("v.push_back({});",
                         generator.element_generator.build_value(self))
        self.writer.block_end()
        self.writer.line("return v;")

    # Values

    def build_values_iterator_type(self, iterator):
        return self.get_autoname(iterator)

    def declare_values_iterator(self, iterator):
        if self.check_declaration_key(iterator):
            return
        output_type = iterator.output_type
        iterator_type = iterator.build_type(self)
        element_type = output_type.build_type(self)
        self.writer.class_begin(iterator_type)
        self.writer.line("public:")
        self.writer.line("typedef {} value_type;", element_type)
        variables = sorted_variables(iterator.get_variables())
        args = ",".join("const {} &{}".format(
                            v.type.build_type(self), v.build_value(self))
                            for v in variables)
        inits = ",".join(("counter(0)",) +
                         tuple("{0}({0})".format(v.name) for v in variables))
        self.writer.line("{}({}) : {} {{}}", iterator_type, args, inits)

        self.writer.line("bool next(value_type &out)")
        self.writer.block_begin()
        self.writer.line("switch(counter)")
        self.writer.block_begin()
        for i, value in enumerate(iterator.values):
            self.writer.line("case {}:", i)
            self.writer.line("out = {};", value.build_value(self))
            self.writer.line("counter++;")
            self.writer.line("return true;")
        self.writer.line("default:")
        self.writer.line("return false;")
        self.writer.block_end()
        self.writer.block_end()

        self.writer.line("void reset()")
        self.writer.block_begin()
        self.writer.line("counter = 0;")
        self.writer.block_end()

        self.write_iterator_write_method()

        self.writer.line("protected:")
        self.writer.line("int counter;")
        for v in variables:
            self.writer.line(
                    "const {} &{};", v.type.build_type(self), v.build_value(self))
        self.writer.class_end()

    def write_values_generator(self, generator):
        self.writer.line("switch(rand() % {})", len(generator.values))
        self.writer.block_begin()
        for i, value in enumerate(generator.values):
            self.writer.line("case {}:", i)
            self.writer.line("return {};", value.build_value(self))
        self.writer.line("default:")
        self.writer.line("assert(0);")
        self.writer.block_end()

    # Function

    def build_function_call(self, function_call):
        function = function_call.function
        function_name = self.get_autoname(function)
        variables = ",".join(v.build_value(self) for v in function.variables)
        args = ",".join(e.build_value(self) for e in function_call.args)
        return "{}({})({})".format(function_name, variables, args)

    def build_functor(self, function):
        function_name = self.get_autoname(function)
        variables = ",".join(v.build_value(self) for v in function.variables)
        return "{}({})".format(function_name, variables)

    def declare_function(self, function):
        if self.check_declaration_key(function):
            return

        if function.is_external():
            self.include_filename(self.env.get_function_filename(function))

        function_name = self.get_autoname(function)
        self.writer.class_begin(function_name)
        self.writer.line("public:")

        if function.variables:
            self.writer.line("{}({}) : {} {{}}",
                             function_name,
                             ",".join("const {} &{}".format(v.type.build_type(self),
                                                      v.name)
                                      for v in function.variables),
                             ",".join("{0}({0})".format(v.name)
                                      for v in function.variables))

        params = [ "const {} &{}".format(type.build_type(self), name)
                   for type, name in function.params ]
        self.writer.line("{} operator()({})",
                         function.return_type.build_type(self),
                         ",".join(params))
        self.writer.block_begin()
        function.write_code(self)
        self.writer.block_end()

        for variable in function.variables:
            self.writer.line("const {} &{};",
                             variable.type.build_type(self),
                             variable.name);

        self.writer.class_end()

    def write_function_from_expression(self, expression):
        self.writer.line("return {};", expression.build_value(self))

    def write_function_inline_code(self, function):
        self.writer.text(function.inline_code)

    def write_function_external_call(self, function):
        call = ""

        if function.return_type is not None:
            call += "return "

        call += function.name + "("
        call += ", ".join([param[1] for param in function.params])  # param names

        self.writer.line(call + ");")

    def get_function_declaration(self, function):
        args = ", ".join([ "const {} &{}".format(c.build_type(self), name)
                   for c, name in function.params ])
        if function.return_type is not None:
            return_type = function.return_type.build_type(self)
        else:
            return_type = "void"
        return "{} {}({})".format(return_type, function.name, args)


    # System

    def declare_system_iterator(self, iterator):
        if self.check_declaration_key(iterator):
           return
        system = iterator.system
        iterator_type = iterator.build_type(self)
        element_iterator_type = system.state_iterator.type.build_type(self)
        element_type = system.state_type.build_type(self)

        variables = sorted_variables(iterator.get_variables())
        args = ",".join(
            "const {} &{}".format(v.type.build_type(self),
                                  v.build_value(self))
            for v in variables)
        inits = ",".join("{0}({0})".format(v.build_value(self))
            for v in variables)
        if args:
            args = "," + args
            inits = "," + inits
        self.writer.class_begin(iterator_type)
        self.writer.line("public:")
        self.writer.line("typedef {} value_type;", element_type)
        self.writer.line("{}(const {} &iterator, int max_depth {}) "
                         ": inited(false), rule(0), depth(0), "
                         "max_depth(max_depth), queue2_emit(0), "
                         " iterator(iterator) {} {{}}",
                         iterator_type, element_iterator_type, args, inits)

        self.writer.line("bool next(value_type &out)")
        self.writer.block_begin()
        self.writer.if_begin("queue2_emit")
        self.writer.line("out = queue2[queue2.size() - queue2_emit--];")
        self.writer.line("return true;")
        self.writer.block_end();
        self.writer.if_begin("!inited")
        self.writer.if_begin("iterator.next(out)")
        self.writer.line("queue1.push_back(out);")
        self.writer.line("discovered.insert(out);")
        self.writer.line("return true;")
        self.writer.block_end()
        self.writer.line("inited = true;")
        self.writer.if_begin("0 == max_depth")
        self.writer.line("return false;")
        self.writer.block_end()
        self.writer.block_end()

        self.writer.line("for(;;)")
        self.writer.block_begin()
        self.writer.if_begin("queue1.size() == 0")
        self.writer.if_begin("queue2.size() == 0")
        self.writer.line("return false;")
        self.writer.block_end()
        self.writer.line("depth++;")
        self.writer.if_begin("depth >= max_depth")
        self.writer.line("return false;")
        self.writer.block_end()
        self.writer.line("std::swap(queue1, queue2);")
        self.writer.block_end()
        self.writer.block_begin()
        self.writer.line("switch(rule)")
        self.writer.block_begin()
        for i, rule in enumerate(system.rules):
            self.writer.line("case {}:", i)
            self.writer.block_begin()
            rule_fn = self.make_instance(
                self.get_autoname(rule),
                "rule_fn",
                [ v.build_value(self)
                  for v in sorted_variables(rule.get_variables())])
            if system.get_rule_type(rule) == RuleType.one_to_one:
                self.writer.line("rule++;")
                self.writer.line("out = {}(queue1.back());", rule_fn, element_type)
                self.writer.if_begin("discovered.find(out) == discovered.end()")
                self.writer.line("discovered.insert(out);")
                self.writer.line("queue2.push_back(out);")
                self.writer.line("return true;")
                self.writer.line("// no break!")
                self.writer.block_end()
            else:
                assert system.get_rule_type(rule) == RuleType.one_to_many
                self.writer.line("rule++;")
                self.writer.line("std::vector<{} > v;", element_type)
                self.writer.line("v = {}(queue1.back());", rule_fn, element_type)
                self.writer.line("size_t found = 0;")
                self.writer.line("for (const auto &i : v)")
                self.writer.block_begin()
                self.writer.if_begin("discovered.find(i) == discovered.end()")
                self.writer.line("discovered.insert(i);")
                self.writer.line("queue2.push_back(i);")
                self.writer.line("found++;")
                self.writer.block_end()
                self.writer.block_end()
                self.writer.if_begin("found")
                self.writer.line("queue2_emit = found - 1;")
                self.writer.line("out = queue2[queue2.size() - found];")
                self.writer.line("return true;")
                self.writer.block_end()
            self.writer.block_end()
        self.writer.line("default: break;")
        self.writer.block_end()
        self.writer.line("rule = 0;")
        self.writer.line("queue2_emit = 0;")
        self.writer.line("queue1.pop_back();")
        self.writer.block_end()
        self.writer.block_end()
        self.writer.block_end()

        self.writer.line("void reset()")
        self.writer.block_begin()
        self.writer.line("inited = false;")
        self.writer.line("rule = 0;")
        self.writer.line("depth = 0;")
        self.writer.line("queue2_emit = 0;")
        self.writer.line("discovered.clear();")
        self.writer.line("queue1.clear();")
        self.writer.line("queue2.clear();")
        self.writer.line("iterator.reset();")
        self.writer.block_end()

        self.write_iterator_write_method()

        self.writer.line("protected:")
        self.writer.line("bool inited;")
        self.writer.line("int rule;")
        self.writer.line("int depth;")
        self.writer.line("int max_depth;")
        self.writer.line("std::vector<{} > queue1;", element_type)
        self.writer.line("std::vector<{} > queue2;", element_type)
        self.writer.line("std::set<{} > discovered;", element_type)
        self.writer.line("size_t queue2_emit;", element_type)
        self.writer.line("{} iterator;", element_iterator_type)
        for v in variables:
            self.writer.line(
                "const {} &{};", v.type.build_type(self), v.build_value(self))
        self.writer.class_end()
