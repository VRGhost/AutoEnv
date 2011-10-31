#!/bin/sh

cd $(dirname "$0")

CUR_BRANCH=$(git branch | grep '*' | sed 's/^* //')

python -m unittest discover -v
TEST_RC=$?

if [ "${TEST_RC}" = "0" ]; then
	# Tests ok
	git checkout master && \
	git merge "${CUR_BRANCH}" --squash -m "Release on $(date -R)" && \
	git checkout "${CUR_BRANCH}"
fi
