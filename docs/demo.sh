#!/usr/bin/env bash
# Scripted simulation of a gmail-cleanup session for demo/GIF recording.
# Fully self-contained — no Gmail auth, no API calls. Just prints the UX.
# Used by docs/demo.tape to render docs/demo.gif via `vhs docs/demo.tape`.

set -e

line() { echo "$1"; sleep 0.25; }

clear
line "$ cat cleanup_plan.json"
cat <<'EOF'
{
  "queries": [
    {"name": "Promotions",     "query": "category:promotions"},
    {"name": "Spam",           "query": "in:spam"},
    {"name": "Old newsletters","query": "older_than:6m label:newsletters"}
  ]
}
EOF
sleep 1

line ""
line "$ python cleanup.py cleanup_plan.json"
sleep 0.4
line "DRY RUN — no emails will be deleted. Pass --execute to actually trash."
line ""
line "Authenticating..."
sleep 0.5
line ""
line "[Promotions]"
line "    fetched 500 ids..."
sleep 0.2
line "    fetched 1000 ids..."
sleep 0.2
line "    fetched 1247 ids..."
line "  1247 matched."
line ""
line "[Spam]"
line "  89 matched."
line ""
line "[Old newsletters]"
line "  312 matched."
line ""
line "=================================================="
line "Dry run complete. Would trash: 1648"
line "Re-run with --execute to actually delete."
sleep 1.2

line ""
line "$ python cleanup.py cleanup_plan.json --execute"
sleep 0.4
line "EXECUTE mode — emails WILL be moved to Trash."
line ""
line "Authenticating..."
sleep 0.3
line ""
line "[Promotions] trashing 1247..."
line "    1000/1247 trashed"
sleep 0.2
line "    1247/1247 trashed"
line "[Spam] trashing 89..."
line "    89/89 trashed"
line "[Old newsletters] trashing 312..."
line "    312/312 trashed"
line ""
line "=================================================="
line "Done. Total trashed: 1648"
line "Logged to .cleanup-history.jsonl (IDs only)."
line "Run \`python cleanup.py --undo\` to restore this run."
sleep 1.5
