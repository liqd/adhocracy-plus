#!/bin/bash
pip install -r requirements/dev.txt

make install
make fixtures

# Activate the virtual environment
source /adhocracy-plus/venv/bin/activate

# Run the make watch command
make watch
