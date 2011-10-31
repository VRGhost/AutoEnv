#!/bin/sh

cd $(dirname "$0")
python -m unittest discover -v
TEST_RC=$?

if [ "${TEST_RC}" = "0" ]; then
	# Tests ok
	git branch master
	git merge master --squash -m "Release on $(date -R)"
fi
