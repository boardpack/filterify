#!/usr/bin/env bash

set -e
set -x

mypy filterify
flake8 filterify tests
black filterify tests --check
isort filterify tests scripts --check-only
