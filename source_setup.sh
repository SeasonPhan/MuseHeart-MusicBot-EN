#!/bin/bash

export PYTHONIOENCODING=utf8

trap 'kill $(jobs -pr)' SIGINT SIGTERM EXIT

echo "Creating VENV (please wait...)"

rm -rf venv

if [ -x "$(command -v py)" ]; then
  py -3 -m venv venv
else
  python3 -m venv venv
fi

if [ ! -d "venv" ]; then
  echo "The venv folder was not created! Please check if you have installed Python correctly (and that it is configured in the PATH/env)"
  sleep 45
  exit 1
fi

if [[ $OSTYPE == "msys" ]]; then
  VENV_PATH=venv/Scripts/activate
else
  VENV_PATH=venv/bin/activate
fi

source $VENV_PATH

mkdir -p ./.logs

touch "./.logs/setup.log"

python -m pip install -U pip

pip install -r ./requirements.txt 2>&1 | tee "./.logs/setup.log"

if [ ! -f ".env" ] && [ ! -f "config.json" ]; then
  cp .example.env .env
  echo "Don't forget to add the necessary tokens to the .env file"
fi

sleep 60s
