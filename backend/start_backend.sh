#!/usr/bin/env bash
# Start the DivyaDrishti backend using a Python 3.11/3.12 virtual environment.
# pyswisseph provides prebuilt wheels for Python 3.11/3.12; using 3.14 or later
# requires a full C/C++ build toolchain and source compilation.
set -e

VENV_PATH="${VENV_PATH:-.venv311}"
PORT="${PORT:-8000}"

PYTHON=""
for py in python3.11 python3.12 python3; do
    if command -v "$py" &>/dev/null; then
        PYTHON="$py"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "Python 3.11 or 3.12 is required. Install it or update your PATH."
    exit 1
fi

PYTHON_VERSION=$($PYTHON --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ ! "$PYTHON_VERSION" =~ ^3\.1[1-2]$ ]]; then
    echo "Detected Python $PYTHON_VERSION. Please use Python 3.11 or 3.12 for pyswisseph compatibility."
    exit 1
fi

if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment at $VENV_PATH ..."
    "$PYTHON" -m venv "$VENV_PATH"
fi

echo "Virtual-env interpreter: $($VENV_PATH/bin/python --version)"
echo "Installing/updating package dependencies ..."
"$VENV_PATH/bin/pip" install -q --disable-pip-version-check -e . 2>/dev/null

echo "Starting uvicorn on port $PORT ..."
"$VENV_PATH/bin/uvicorn" divyadrishti.main:app --reload --host 0.0.0.0 --port "$PORT"
