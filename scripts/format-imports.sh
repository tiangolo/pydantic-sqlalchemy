#!/bin/sh -e
set -x

# Sort imports one per line, so autoflake can remove unused imports
isort --recursive  --force-single-line-imports --thirdparty sqlalchemy_dantic --apply ./sqlalchemy_dantic ./tests
sh ./scripts/format.sh
