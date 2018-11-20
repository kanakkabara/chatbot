#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cd $DIR/intent
snips-nlu generate-dataset en $(ls -t $DIR/intent) > $DIR/dataset/dataset.json