import importlib.abc
import sys
import pathlib
from os.path import (
    exists as path_exists,
    join as join_path,
)
import types


class ImportStubberLoader(importlib.abc.Loader):
    def __init__(self, _COMMON_PREFIX="__generated_sample."):
        self._COMMON_PREFIX = _COMMON_PREFIX
        self._services = {}
        # create a dummy module to return when Python attempts to import
        # myapp and myapp.virtual, the :-1 removes the last "." for
        # aesthetic reasons :)
        self._dummy_module = types.ModuleType(self._COMMON_PREFIX[:-1])
        # set __path__ so Python believes our dummy module is a package
        # this is important, since otherwise Python will believe our
        # dummy module can have no submodules
        self._dummy_module.__path__ = []

    def provide(self, service_name, module):
        """Register a service as provided via the given module
        A service is any Python object in this context - an imported module,
        a class, etc."""
        self._services[service_name] = module

    def provides(self, fullname):
        return fullname.startswith(self._COMMON_PREFIX)

    def create_module(self, spec):
        """Create the given module from the supplied module spec
        Under the hood, this module returns a service or a dummy module,
        depending on whether Python is still importing one of the names listed
        in _COMMON_PREFIX.
        """
        service_name = self._truncate_name(spec.name)
        path_name = '/'.join(spec.name.split('.'))
        path_name_with_py = f"{path_name}.py"
        joined_py_paths = [
            join_path(p, path_name_with_py) for p in sys.path
        ]
        for _p in joined_py_paths:
            if path_exists(_p):
                with open(_p, 'r') as f:
                    return f.read()
        path_name_with_init = f"{path_name}/__init__.py"
        joined_init_paths = [
            join_path(p, path_name_with_init) for p in sys.path
        ]

        for _p in joined_init_paths:
            if path_exists(_p):
                with open(_p, 'r') as f:
                    return f.read()
        return self._dummy_module
        #
        # if service_name not in self._services:
        #     # return our dummy module since at this point we're loading
        #     # *something* along the lines of "myapp.virtual" that's not
        #     # a service
        #     return self._dummy_module
        # module = self._services[service_name]
        # print(module)
        # return module

    def exec_module(self, module):
        """Execute the given module in its own namespace
        This method is required to be present by importlib.abc.Loader,
        but since we know our module object is already fully-formed,
        this method merely no-ops.
        """
        pass

    def _truncate_name(self, fullname):
        """Strip off _COMMON_PREFIX from the given module name
        Convenience method when checking if a service is provided.
        """
        return fullname[len(self._COMMON_PREFIX):]
