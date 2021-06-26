#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place ./sqlalchemy_dantic ./tests --exclude=__init__.py
black ./sqlalchemy_dantic ./tests
isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 --recursive --thirdparty sqlalchemy_dantic --apply ./pydantic_sqlalchemy ./tests
