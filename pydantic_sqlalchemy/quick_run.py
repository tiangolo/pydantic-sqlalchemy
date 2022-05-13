

from pydantic_sqlalchemy import extract_from_sqlalchemy
from pydantic_sqlalchemy.models_collector import ModelsCollector
from tests.fixtures.Address import Address
from tests.fixtures.User import User

if __name__ == '__main__':
    import os
    os.system('cls' if os.name == 'nt' else 'clear')
    collector = ModelsCollector()
    collected = collector.collect(User)
    import pprint
    pprint.pprint(collected)