
from qit.build.builder import CppBuilder
from qit.base.utils import makedir_if_not_exists
from qit.base.exception import MissingFiles, ProgramCrashed

import tempfile
import os
import subprocess
import logging


LOG = logging.getLogger("qit")


class CppEnv(object):

    def __init__(self, qit):
        self.qit = qit
        self.build_dir = os.path.abspath(qit.build_dir)
        self.compiler = "/usr/bin/g++"
        self.cpp_flags = ("-O3",
                          "-std=c++11",
                          "-march=native")

    def run_collect(self, exprs, args):
        for expr in exprs:
            self.check_all(expr)
        builder = CppBuilder(self)
        builder.build_collect(exprs, args)
        return self.compile_builder(builder, [expr.type for expr in exprs])

    def get_file(self):
        makedir_if_not_exists(self.build_dir)
        if self.qit.debug:
            filename = os.path.join(self.build_dir, "debug.cpp")
            return open(filename, "w")
        else:
            return tempfile.NamedTemporaryFile(
                      mode="w",
                      prefix="qit-",
                      suffix=".cpp",
                      dir=self.build_dir,
                      delete=False)

    def compile_builder(self, builder, types):
        text = builder.writer.get_string()
        makedir_if_not_exists(self.build_dir)
        with self.get_file() as f:
            filename = f.name
            logging.debug("Creating file %s", filename)
            f.write(text)
        exe_filename = filename[:-4]
        args = (self.compiler, "-o", exe_filename, filename) + self.cpp_flags
        subprocess.check_call(args)
        fifo_name = exe_filename + "-fifo"
        return self.run_program(exe_filename, fifo_name, types)

    def run_program(self, exe_filename, fifo_name, types):
        if fifo_name:
            os.mkfifo(fifo_name)
            try:
                args = (exe_filename, fifo_name,)
                logging.debug("Running: %s", args)
                popen = subprocess.Popen(
                        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                with open(fifo_name, "rb") as f:
                    if len(types) == 1:
                        result = types[0].read(f)
                    else:
                        result = [ t.read(f) for t in types ]
                stdout, stderr = popen.communicate()
                if popen.returncode != 0:
                    raise ProgramCrashed(stdout, stderr)
                return result
            finally:
                os.unlink(fifo_name)
        else:
            args = (exe_filename,)
            logging.debug("Running: %s", args)
            subprocess.check_call(args)

    def declarations(self, obj):
        builder = CppBuilder(self)
        return [builder.get_function_declaration(fn) for fn in obj.get_functions()
                if fn.is_external()]

    def get_function_filename(self, function):
        return os.path.abspath(
                os.path.join(self.qit.source_dir, function.filename))

    def get_function_filenames(self, functions):
        filenames = {}
        for function in functions:
            if function.is_external():
                filename = self.get_function_filename(function)
                if filename in filenames:
                    filenames[filename].append(function)
                else:
                    filenames[filename] = [function]
        return filenames

    def get_missing_function_filenames(self, functions):
        result = {}
        for filename, functions in \
                self.get_function_filenames(functions).items():
            if not os.path.isfile(filename):
                result[filename] = functions
        return result

    def check_all(self, iterator):
        self.check_functions(iterator)

    def check_functions(self, iterator):
        functions = iterator.get_functions()
        missing_filenames = self.get_missing_function_filenames(functions)
        if not missing_filenames:
            return
        if self.qit.auto_create_files:
            self.create_source_files(iterator)
        builder = CppBuilder(self)
        filenames = list(sorted(missing_filenames.keys()))
        functions = sum(missing_filenames.values(), [])
        message = "File(s) {} are required because " \
                  "of the following function(s):\n {}\n".format(
                          ",".join(filenames),
                          ",".join(builder.get_function_declaration(f)
                                   for f in functions))
        raise MissingFiles(message, filenames)

    def create_source_files(self, obj):
        builder = CppBuilder(self)
        filenames = self.get_missing_function_filenames(obj.get_functions())
        for path, functions in filenames.items():
            logging.warning("Creating file %s", path)
            with open(path, "w") as f:
                for fn in functions:
                    f.write(builder.get_function_declaration(fn))
                    f.write("\n{\n\n}\n\n")
