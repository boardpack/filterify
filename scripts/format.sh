#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place filterify tests scripts --exclude=__init__.py
black filterify tests scripts
isort filterify tests scripts
