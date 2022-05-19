from pprint import pprint

from pydantic_sqlalchemy import extract_from_sqlalchemy
from pydantic_sqlalchemy.codegen_from_collected_models import collected_file_to_pydantic_file
from pydantic_sqlalchemy.models_collector import ModelsCollector
from tests.fixtures.Address import Address
from tests.fixtures.User import User

if __name__ == '__main__':
    import os
    os.system('cls' if os.name == 'nt' else 'clear')
    collector = ModelsCollector()
    collected = collector.collect(User)
    # print('collected:...')
    # pprint(collected)

    for module_path, collected_file in collected.items():
        # pprint(collected_file_to_pydantic_file(collected_file))
        print(collected_file_to_pydantic_file(collected_file).render())
        print('--------')