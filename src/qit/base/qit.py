from qit.build.builder import CppBuilder
from qit.build.env import CppEnv

import logging

LOG = logging.getLogger("qit")

class Qit:

    def __init__(self,
                 source_dir=".",
                 build_dir="./qit-build",
                 verbose=None,
                 create_files=False,
                 debug=False):
        self.debug = debug
        self.source_dir = source_dir
        self.build_dir = build_dir
        self.auto_create_files = create_files
        self.env = CppEnv(self)

        log_level = None
        if verbose == 1:
            log_level = logging.INFO
        elif verbose == 2:
            log_level = logging.DEBUG
        elif verbose == 0:
            log_level = logging.ERROR
        elif verbose is not None:
            LOG.warning("Invalid logging level")

        if log_level is not None:
            logging.basicConfig(format="%(levelname)s: %(message)s",
                                level=log_level)

    def run(self, iterator):
        return self.env.run_collect(iterator)

    def declarations(self, obj, exclude_inline=True):
        if not hasattr(obj, "get_functions"):
            raise TypeError(
                    repr(obj) + " does not have attribute 'get_functions'")
        return self.env.declarations(obj, exclude_inline=exclude_inline)

    def create_files(self, obj):
        if not hasattr(obj, "get_functions"):
            raise TypeError(
                    repr(obj) + " does not have attribute 'get_functions'")
        self.env.create_source_files(obj)
