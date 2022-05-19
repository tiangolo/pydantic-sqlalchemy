import sys

from pydantic_sqlalchemy.stub_imports_before_codegen.import_stubber_finder import ImportStubberFinder
from pydantic_sqlalchemy.stub_imports_before_codegen.import_stubber_loader import ImportStubberLoader


class ImportStubberInstaller:
    """
    Convenience wrapper for DependencyInjectorLoader and DependencyInjectorFinder.
    """

    def __init__(self):
        self._loader = ImportStubberLoader()
        self._finder = ImportStubberFinder(self._loader)

    def install(self):
        sys.meta_path.append(self._finder)

    def provide(self, service_name, module):
        self._loader.provide(service_name, module)
