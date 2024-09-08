#!/usr/bin/env bash

set -e
set -x

mypy pydantic_sqlalchemy
ruff check pydantic_sqlalchemy tests scripts
ruff format sqlmpydantic_sqlalchemyodel tests scripts --check
