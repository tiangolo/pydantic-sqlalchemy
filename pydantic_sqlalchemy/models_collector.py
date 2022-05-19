from dataclasses import dataclass, field
from dataclasses import dataclass, field
from typing import Type, NewType, Dict, Set, List

from pydantic_sqlalchemy import extract_from_sqlalchemy
from pydantic_sqlalchemy.extract_from_sqlalchemy import GeneratedImportReference, ExtractedModel
from pydantic_sqlalchemy.module_path_typ import ModulePathType, get_module_path


@dataclass
class CollectedFile:
    module: ModulePathType
    models: Set[ExtractedModel] = field(default_factory=set)
    imports: Set[GeneratedImportReference] = field(default_factory=set)


@dataclass
class ModelsCollector:
    collected_files: Dict[ModulePathType, CollectedFile] = field(default_factory=dict)
    visited_raw: Set[Type] = field(default_factory=set)
    queue_raw: List[Type] = field(default_factory=list)
    # extracted_models: Set[ExtractedModel] = field(default_factory=set)

    def ref_from_sqlalchemy_model(self, model: Type):
        ...

    def write_to_dir(self):
        ...

    def override_fields(self, raw_model: Type, fields: ...):
        ...

    def collect(self, raw_model: Type):
        self.queue_raw.append(raw_model)
        while True:
            if len(self.queue_raw) == 0:
                break
            elem = self.queue_raw.pop()
            if elem is None:
                break

            if elem not in self.visited_raw:
                self.visited_raw.add(elem)
                result = extract_from_sqlalchemy(elem)

                module_path = get_module_path(elem)
                collected_file = self.collected_files.get(
                    module_path,
                    CollectedFile(module=module_path)
                )
                collected_file.models.add(result)
                for dep in result.depends_on:
                    if isinstance(dep, GeneratedImportReference):
                        self.queue_raw.append(dep.original)
                        collected_file.imports.add(dep)
                    else:
                        self.queue_raw.append(dep)
                self.collected_files[module_path] = collected_file
        return self.collected_files

