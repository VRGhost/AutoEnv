#!/bin/sh

cd $(dirname "$0")
python -m unittest discover -v
