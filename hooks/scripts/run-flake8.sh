#!/bin/sh
staged_files=$(git diff --staged --name-only HEAD --diff-filter=ACMR | grep -E '\.py$')
riot -v run -s flake8 $staged_files
