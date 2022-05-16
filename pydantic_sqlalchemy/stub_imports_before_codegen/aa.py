from pydantic_sqlalchemy.stub_imports_before_codegen.import_stubber_finder import ImportStubberFinder
from pydantic_sqlalchemy.stub_imports_before_codegen.import_stubber_loader import ImportStubberLoader

import sys


class DependencyInjector:
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


class FrontendModule:
    class Popup:
        def __init__(self, message):
            self._message = message

        def display(self):
            print("Popup:", self._message)


if __name__ == '__main__':
    injector = DependencyInjector()
    injector.install()

    print('!!importing!')
    print('~~~~~~~~')
    import __generated_sample.hello as _generated__hello
    print(_generated__hello)
    import __generated_sample.not_existing as _generated__not_existing
    print(_generated__not_existing)
    # import myapp.virtual.not_frontend as not_frontend
    # print(not_frontend)