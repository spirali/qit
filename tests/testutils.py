import os
import sys

TEST_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(TEST_DIR)
SRC_DIR = os.path.join(ROOT_DIR, "src")
BUILD_DIR = os.path.join(TEST_DIR, "build")

def init():
    if SRC_DIR not in sys.path:
        sys.path.append(SRC_DIR)
    if not os.path.isdir(BUILD_DIR):
        os.makedirs(BUILD_DIR)

def Qit():
    import qit
    return qit.Qit(debug=True, build_dir=BUILD_DIR)
