
from qit.build.builder import CppBuilder
from qit.utils.fs import makedir_if_not_exists
from qit.base import paths

import tempfile
import os
import subprocess


class CppEnv(object):

    def __init__(self):
        self.build_dir = os.path.join(os.getcwd(), "qit-build")
        self.compiler = "g++"
        self.cpp_flags = ("-O3",
                          "-march=native",
                          "-I", paths.LIBQIT_DIR)

    def run_print_all(self, collection):
        builder = CppBuilder()
        builder.build_print_all(collection)
        self.compile_builder(builder)

    def compile_builder(self, builder):
        text = builder.writer.get_string()
        data = bytes(text, "UTF-8")
        makedir_if_not_exists(self.build_dir)
        with tempfile.NamedTemporaryFile(
                prefix="qit-",
                suffix=".cpp",
                dir=self.build_dir,
                delete=False) as f:
            filename = f.name
            print("Creating file: {}".format(filename))
            f.write(data)
        exe_filename = filename[:-4]
        args = (self.compiler, "-o", exe_filename, filename) + self.cpp_flags
        print("Running: " + " ".join(args))
        subprocess.check_call(args)
        args = (exe_filename,)
        print("Running: " + " ".join(args))
        subprocess.check_call(args)
