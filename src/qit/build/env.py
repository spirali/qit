
from qit.build.builder import CppBuilder
from qit.utils.fs import makedir_if_not_exists
from qit.base import paths

import tempfile
import os
import subprocess


class CppEnv(object):

    def __init__(self, qit):
        self.qit = qit
        self.build_dir = os.path.abspath(qit.build_dir)
        self.compiler = "g++"
        self.cpp_flags = ("-O3",
                          "-std=c++11",
                          "-march=native",
                          "-I", paths.LIBQIT_DIR)

    def run_collect(self, iterator):
        builder = CppBuilder(self.qit)
        builder.build_collect(iterator)
        return self.compile_builder(builder, iterator.output_type.basic_type)

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

    def compile_builder(self, builder, type):
        text = builder.writer.get_string()
        makedir_if_not_exists(self.build_dir)
        with self.get_file() as f:
            filename = f.name
            print("Creating file: {}".format(filename))
            f.write(text)
        exe_filename = filename[:-4]
        args = (self.compiler, "-o", exe_filename, filename) + self.cpp_flags
        subprocess.check_call(args)
        if type:
            fifo_name = exe_filename + "-fifo"
        else:
            fifo_name = None
        return self.run_program(exe_filename, fifo_name, type)

    def run_program(self, exe_filename, fifo_name, type):
        if fifo_name:
            os.mkfifo(fifo_name)
            try:
                args = (exe_filename, fifo_name,)
                print("Running: " + " ".join(args))
                popen = subprocess.Popen(args)
                with open(fifo_name, "rb") as f:
                    result = list(type.read_all(f))
                popen.wait()
                return result
            finally:
                os.unlink(fifo_name)
        else:
            args = (exe_filename,)
            print("Running: " + " ".join(args))
            subprocess.check_call(args)

