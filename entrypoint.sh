#!/bin/bash
# Activate the virtual environment
source /adhocracy-plus/venv/bin/activate
pip install -r requirements/dev.txt

make install
make fixtures
# Run the make watch command
make watch
