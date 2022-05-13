from collections import deque
from dataclasses import dataclass, field
from queue import Queue
from typing import Type, NewType, Dict, Set, Deque, List

from pydantic_sqlalchemy import extract_from_sqlalchemy
from pydantic_sqlalchemy.extract_from_sqlalchemy import ExtractedModel

FilePathType = NewType('FilePathType', str)

CollectedFileRefType = NewType('CollectedModelRefType', str)


@dataclass
class CollectedFile:
    file_path: str
    imports: Set[CollectedFileRefType] = field(default_factory=set)


@dataclass
class ModelsCollector:
    collected_models: Dict[CollectedFileRefType, CollectedFile] = field(default_factory=dict)
    visited_raw: Set[Type] = field(default_factory=set)
    queue_raw: List[Type] = field(default_factory=list)
    extracted_models: Set[ExtractedModel] = field(default_factory=set)

    def ref_from_sqlalchemy_model(self, model: Type):
        ...

    def write_to_dir(self):
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
                self.extracted_models.add(result)
                for dep in result.depends_on:
                    print("Appending: ", dep)
                    self.queue_raw.append(dep)
        return result

