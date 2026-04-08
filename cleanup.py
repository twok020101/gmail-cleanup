#!/usr/bin/env python3
"""
Gmail Cleanup — backward-compatible shim.

This file exists so that existing users and the setup.sh / CLAUDE.md
workflows can continue to invoke `python cleanup.py plan.json [flags]`
unchanged.

All real logic now lives in the `gmail_cleanup` package (src/gmail_cleanup/).
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _ensure_venv() -> None:
    """Re-exec under the repo venv if we're not already running inside it."""
    venv_py = None
    for rel in ["venv/bin/python", "venv/Scripts/python.exe"]:
        full = os.path.join(SCRIPT_DIR, rel)
        if os.path.exists(full):
            venv_py = full
            break
    if not venv_py:
        print("ERROR: venv not found. Run: bash setup.sh")
        sys.exit(1)
    if os.path.realpath(sys.executable) != os.path.realpath(venv_py):
        os.execv(venv_py, [venv_py, os.path.abspath(__file__)] + sys.argv[1:])


_ensure_venv()

# After re-exec we're running under the venv Python, so the package is importable.
from gmail_cleanup.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
