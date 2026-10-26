#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
python3 verify_kit.py
python3 -m venv .venv
.venv/bin/python -m pip --disable-pip-version-check install --force-reinstall --no-index --find-links wheels breakguard=={{VERSION}}
.venv/bin/breakguard --version
