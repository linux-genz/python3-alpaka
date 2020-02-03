#!/bin/bash
TEST_FILE="$( cd "$(dirname "$0")" ; pwd -P )/test_target.sh"

test_files=$(find . -name 'test_*.py')

for i in $test_files; do
  $i
done