from dataclasses import dataclass, field
from typing import Type, NewType, Dict, Set

FilePathType = NewType('FilePathType', str)

CollectedModelRefType = NewType('CollectedModelRefType', str)


@dataclass
class CollectedModel:
    file_path: str
    imports: Set[CollectedModelRefType] = field(default_factory=set)


@dataclass
class ModelsCollector:
    collected_models: Dict[CollectedModelRefType, CollectedModel] = field(default_factory=dict)

    def ref_from_sqlalchemy_model(self, model: Type):
        ...

    def write_to_dir(self):
        ...

    def collect(self):
        pass
