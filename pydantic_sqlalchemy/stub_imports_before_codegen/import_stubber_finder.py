import importlib.abc
import importlib.machinery


class ImportStubberFinder(importlib.abc.MetaPathFinder):
    def __init__(
            self,
            loader,
    ):
        # we'll write the loader in a minute, hang tight
        self._loader = loader
        self.already_generated_files = False

    def find_spec(self, fullname, path, target=None):
        """Attempt to locate the requested module
        fullname is the fully-qualified name of the module,
        path is set to __path__ for sub-modules/packages, or None otherwise.
        target can be a module object, but is unused in this example.
        """
        if self._loader.provides(fullname):
            return self._gen_spec(fullname)

    def _gen_spec(self, fullname):
        spec = importlib.machinery.ModuleSpec(fullname, self._loader)
        return spec
