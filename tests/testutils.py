import os
import sys
import shutil

TEST_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(TEST_DIR)
SRC_DIR = os.path.join(ROOT_DIR, "src")
BUILD_DIR = os.path.join(TEST_DIR, "build")

def init():
    if SRC_DIR not in sys.path:
        sys.path.insert(0, SRC_DIR)
    if not os.path.isdir(BUILD_DIR):
        os.makedirs(BUILD_DIR)

def cleanup_build_dir():
    if os.path.isdir(BUILD_DIR):
        for item in os.listdir(BUILD_DIR):
            path = os.path.join(BUILD_DIR, item)
            if os.path.isfile(path):
                os.unlink(path)
            else:
                shutil.rmtree(path)

def get_filename_in_build_dir(filename):
    return os.path.join(BUILD_DIR, filename)

def get_file_in_build_dir(filename, mode="r"):
    return open(get_filename_in_build_dir(filename), mode)

def make_file_in_build_dir(filename, content=""):
    with get_file_in_build_dir(filename, "w") as f:
        f.write(content)

def Qit(create_files=False):
    cleanup_build_dir()
    import qit
    return qit.Qit(debug=True,
                   create_files=create_files,
                   build_dir=BUILD_DIR,
                   source_dir=BUILD_DIR)
