
from qit.build.builder import CppBuilder
from qit.utils.fs import makedir_if_not_exists
from qit.base import paths

import tempfile
import os
import subprocess


class CppEnv(object):

    def __init__(self, qit):
        self.qit = qit
        self.build_dir = os.path.join(os.getcwd(), "qit-build")
        self.compiler = "g++"
        self.cpp_flags = ("-O3",
                          "-std=c++11",
                          "-march=native",
                          "-I", paths.LIBQIT_DIR)

    def run_print_all(self, collection):
        builder = CppBuilder()
        builder.build_print_all(collection)
        self.compile_builder(builder)

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


    def compile_builder(self, builder):
        text = builder.writer.get_string()
        makedir_if_not_exists(self.build_dir)
        with self.get_file() as f:
            filename = f.name
            print("Creating file: {}".format(filename))
            f.write(text)
        exe_filename = filename[:-4]
        args = (self.compiler, "-o", exe_filename, filename) + self.cpp_flags
        print("Running: " + " ".join(args))
        subprocess.check_call(args)
        args = (exe_filename,)
        print("Running: " + " ".join(args))
        subprocess.check_call(args)
