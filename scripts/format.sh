#!/bin/sh -e
set -x

ruff check pydantic_sqlalchemy tests scripts --fix
ruff format pydantic_sqlalchemy tests scripts
