#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place ./pydantic_sqlalchemy ./tests --exclude=__init__.py
black ./pydantic_sqlalchemy ./tests
isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 --recursive --thirdparty pydantic_sqlalchemy --apply ./pydantic_sqlalchemy ./tests
