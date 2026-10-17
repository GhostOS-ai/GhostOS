#!/usr/bin/env bash
# GhostOS Fast Launcher
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
export PYTHONPATH="$DIR:$PYTHONPATH"
python3 -m ghost "$@"
