
from qit.build.writer import CppWriter
from qit.base.utils import sorted_variables
from qit.base.utils import validate_variables, sort_by_deps
from qit.base.exception import QitException
import jinja2

class CppBuilder(object):

    def __init__(self, env):
        self.env = env
        self.writer = CppWriter()
        self.declaration_keys = []
        self.names = {}
        self.ids = set()
        self.included_filenames = set()

    def get_name(self, obj):
        name = self.names.get(obj)
        if name is not None:
            return name
        obj_name = obj.name
        name = self.new_id(obj_name)
        self.names[obj] = name
        return name

    def include_filename(self, filename):
        if filename in self.included_filenames:
            return
        self.included_filenames.add(filename)
        self.writer.line("#include \"{}\"", filename)

    def get_used_variables(self, exprs, args):
        variables = frozenset()
        for expr in exprs:
            variables = variables.union(expr.get_variables())
        prev = frozenset()
        while prev != variables:
            prev = variables
            for v in variables:
                a = args.get(v)
                if a is None:
                    raise QitException("Unbound variable '{}'".format(v))
                variables = variables.union(a.get_variables())
        return variables

    def build_collect(self, exprs, args):
        variables = self.get_used_variables(exprs, args)
        validate_variables(variables)
        deps = { v: args[v].get_variables() for v in variables }
        variables = sort_by_deps(deps)

        write_functions = [ expr.type.write_function for expr in exprs ]
        self.write_header()
        for v in variables:
            args[v].declare_all(self)
        for expr in exprs:
            expr.declare_all(self)
        for f in write_functions:
            f.declare_all(self)
        self.main_begin()
        self.init_fifo()
        self.init_variables(variables, args)
        for expr, f in zip(exprs, write_functions):
            self.writer.line(
                 "{}(output, {});", f.build(self), expr.build(self))
        self.writer.line("fclose(output);")
        self.main_end()

    def write_expression_into_variable(self, expr):
        variable = self.new_id()
        self.writer.line("{} {} = {};",
                         expr.type.build(self),
                         variable,
                         expr.build(self))
        return variable

    def build_object(self, type, args):
        args = ",".join(a.build(self) for a in args)
        return "{}({})".format(type.build(self), args)

    def write_iterator_write_method(self):
        self.writer.line("QIT_ITERATOR_WRITE_METHOD")

    def make_sequence_from_iterator(self, iterator):
        result_variable = self.new_id("result")
        self.writer.line("{} {};",
                         iterator.output_type.build(self),
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

    def init_variables(self, variables, args):
        for variable in variables:
            value = args[variable]
            self.writer.line("{} {}({});",
                             variable.type.build(self),
                             variable.build(self),
                             value.build(self))

    def write_header(self):
        self.writer.line("/*")
        self.writer.line("       QIT generated file")
        self.writer.line("*/")
        self.writer.emptyline()
        self.writer.line("#include <vector>")
        self.writer.line("#include <deque>")
        self.writer.line("#include <set>")
        self.writer.line("#include <map>")
        self.writer.line("#include <iostream>")
        self.writer.line("#include <assert.h>")
        self.writer.line("#include <stdlib.h>")
        self.writer.line("#include <time.h>")
        self.writer.line("#include <algorithm>")
        self.writer.line("#include <random>")
        self.writer.emptyline()
        self.writer.line("std::default_random_engine QIT_GENERATOR(time(nullptr));")
        self.writer.line("typedef int32_t qint;")
        self.writer.emptyline()
        self.writer.emptyline()

    def main_begin(self):
        self.writer.line("int main(int argc, char **argv)")
        self.writer.block_begin()
        self.writer.line("srand(time(NULL));")

    def main_end(self):
        self.writer.line("return 0;")
        self.writer.block_end();

    def new_id(self, name):
        prefix = "q_" + name
        s = ""
        while prefix[-1].isdigit():
            s += prefix[-1]
            prefix = str(prefix[:-1])
        if s:
            suffix = int(s) + 1
        else:
            suffix = 1

        name = prefix + str(suffix)
        while name in self.ids:
            suffix += 1
            name = prefix + str(suffix)
        self.ids.add(name)
        return name

    ## Method for multiple dispatch of base classes

    def check_declaration_key(self, key):
        if key in self.declaration_keys:
            return True
        self.declaration_keys.append(key)
        self.writer.line("/* Declaration: {} */", key)
        return False

    # Struct

    def declare_struct(self, struct):
        if self.check_declaration_key(struct):
            return
        struct_type = struct.build(self)
        self.writer.class_begin(struct_type)
        self.writer.line("public:")

        ## Attributes
        for name, t in zip(struct.names, struct.types):
            self.writer.line("{} {};",
                             t.build(self),
                             name)

        if struct.names:
            params = ",".join(t.build_param(self, name)
                            for t, name in zip(struct.types, struct.names))

            consts = ": " + ",".join("{0}({0})".format(name)
                            for name in struct.names)
            self.writer.line("{}({}) {} {{}}", struct_type, params, consts)
        self.writer.line("{}() {{}}", struct_type)

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
        if struct.names:
            self.writer.line("return {};",
                             " && ".join("({0} == other.{0})".format(name)
                                 for name in struct.names))
        else:
            self.writer.line("return true;")
        self.writer.block_end()
        self.writer.class_end()

    # Function

    def build_function_call(self, function_call):
        functor = self.build_functor(function_call.function)
        args = ",".join(e.build(self) for e in function_call.args)
        return "{}({})".format(functor, args)

    def build_functor(self, function, prefix=""):
        function_name = self.get_name(function)
        variables = sorted_variables(function.get_variables())
        if variables:
            v = ",".join(prefix + v.build(self) for v in variables)
            return "({}({}))".format(function_name, v)
        else:
            return "{}".format(function_name)

    def declare_function(self, function):
        if self.check_declaration_key(function):
            return

        function_name = self.get_name(function)
        variables = function.get_variables()

        if function.is_external():
            self.include_filename(self.env.get_function_filename(function))

        if not variables:
            decl = function.build_declaration(self, function_name)
            self.writer.line("{}", decl)
            self.writer.block_begin()
            function.write_code(self)
            self.writer.block_end()
            self.writer.emptyline()
            return
        variables = sorted_variables(variables)

        self.writer.class_begin(function_name)
        self.writer.line("public:")
        variables = sorted_variables(variables)
        self.writer.line("{}({}) : {} {{}}",
                         function_name,
                         ",".join("const {} &{}".format(v.type.build(self),
                                                  v.build(self))
                                  for v in variables),
                         ",".join("{0}({0})".format(v.build(self))
                                  for v in variables))
        self.writer.line("{}", function.build_declaration(self, "operator()"))
        self.writer.block_begin()
        function.write_code(self)
        self.writer.block_end()

        for variable in variables:
            self.writer.line("const {} &{};",
                             variable.type.build(self),
                             variable.build(self));

        self.writer.class_end()
        self.writer.emptyline()

    def write_return_expression(self, expression):
        self.writer.line("return {};", expression.build(self))

    def write_code(self, inline_code, inline_code_vars):
        if isinstance(inline_code_vars, dict):
            inline_code_vars = tuple(inline_code_vars.items())
        d = {}
        for name, obj in inline_code_vars:
            if name.startswith("_"):
                d[name] = obj
            else:
                d[name] = obj.build(self)
        template = jinja2.Template(inline_code)
        template.globals.update(b=lambda obj: obj.build(self))
        template.globals["_builder"] = self
        self.writer.text(template.render(d))

    def write_function_external_call(self, function):
        call = ""

        if function.return_type is not None:
            call += "return "

        call += function.name + "("
        call += ", ".join([param.name for param in function.params])  # param names

        self.writer.line(call + ");")

    def get_function_declaration(self, function):
        args = ", ".join(p.type.build_param(self, p.name, p.const)
                         for p in function.params)
        if function.return_type is not None:
            return_type = function.return_type.build(self)
        else:
            return_type = "void"
        return "{} {}({})".format(return_type, function.name, args)
