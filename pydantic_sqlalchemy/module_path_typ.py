import os
from typing import NewType, Type, List

ModulePathType = NewType('ModulePathType', str)


def get_module_path(raw: Type):
    return ModulePathType(raw.__module__)


def module_path_to_file_path(module_path: ModulePathType):
    return '/'.join(module_path.split('.'))


def get_mangled_module_path_as_name(module_path: ModulePathType):
    return '__'.join(module_path.split('.'))


def get_child_modules_path(module_path: ModulePathType):
    to_return: List[ModulePathType] = []
    splitted = module_path.split('.')
    for i in splitted:
        if len(to_return) == 0:
            to_return.append(ModulePathType(i))
        else:
            last = to_return[-1]
            to_return.append(ModulePathType(f"{last}.{i}"))
    return to_return


def to_fs_path(
        module_path: ModulePathType,
        base_path: str,
):
    return os.path.join(
        base_path,
        *(module_path.split('.'))
    )
