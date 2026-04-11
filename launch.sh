#!/usr/bin/env bash
# SudokuSolver launcher (Linux/macOS) - NAS-portable
# Venv lives in $XDG_DATA_HOME/SudokuSolver/venv (local per PC)

set -e
APP_NAME="SudokuSolver"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
VENV_DIR="$DATA_HOME/$APP_NAME/venv"
DEPS_MARKER="$VENV_DIR/.deps_installed"
REQ_FILE="$PROJECT_DIR/requirements.txt"

# Detect Python
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD=python
else
    echo "[ERROR] Python 3.10+ not found" >&2
    exit 1
fi

# Create venv if missing or broken
need_create=0
if [ ! -x "$VENV_DIR/bin/python" ]; then
    need_create=1
elif ! "$VENV_DIR/bin/python" -c "print('ok')" >/dev/null 2>&1; then
    need_create=1
fi
if [ "$need_create" = "1" ]; then
    echo "[INFO] Creating venv at $VENV_DIR"
    mkdir -p "$(dirname "$VENV_DIR")"
    rm -rf "$VENV_DIR"
    "$PYTHON_CMD" -m venv "$VENV_DIR"
    rm -f "$DEPS_MARKER"
fi

# Install deps if requirements.txt changed
need_install=0
if [ ! -f "$DEPS_MARKER" ]; then
    need_install=1
elif ! cmp -s "$REQ_FILE" "$DEPS_MARKER"; then
    need_install=1
fi
if [ "$need_install" = "1" ]; then
    echo "[INFO] Installing dependencies"
    "$VENV_DIR/bin/python" -m pip install --upgrade pip >/dev/null
    "$VENV_DIR/bin/python" -m pip install -r "$REQ_FILE"
    cp "$REQ_FILE" "$DEPS_MARKER"
fi

exec "$VENV_DIR/bin/python" "$PROJECT_DIR/main.py" "$@"
