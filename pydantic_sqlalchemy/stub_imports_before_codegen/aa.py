from pydantic_sqlalchemy.stub_imports_before_codegen.import_stubber_installer import ImportStubberInstaller

if __name__ == '__main__':
    injector = ImportStubberInstaller()
    injector.install()

    print('!!importing!')
    print('~~~~~~~~')
    import __generated_sample.hello as _generated__hello
    print(_generated__hello)
    import __generated_sample.not_existing as _generated__not_existing
    print(_generated__not_existing)
    # import myapp.virtual.not_frontend as not_frontend
    # print(not_frontend)