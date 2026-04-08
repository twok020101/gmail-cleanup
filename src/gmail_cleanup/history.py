"""
History tracking for cleanup runs.

History file is anchored to the current working directory (os.getcwd()), NOT to the
package install path. This allows pipx-installed users to keep history alongside
their credentials.json in whatever directory they run gmail-cleanup from.
"""

import json
import os
from typing import Optional

# Resolved at call-time (not import-time) so cwd can change between calls if needed.
HISTORY_FILENAME = ".cleanup-history.jsonl"


def _history_path() -> str:
    """Return absolute path to the history file in the current working directory."""
    return os.path.join(os.getcwd(), HISTORY_FILENAME)


def append_history(entry: dict) -> None:
    """Append a JSON entry (one line) to the history file."""
    path = _history_path()
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def read_last_history_entry() -> Optional[dict]:
    """Return the last line of the history file as a dict, or None if empty/missing."""
    path = _history_path()
    if not os.path.exists(path):
        return None
    last = None
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                last = json.loads(line)
    return last
