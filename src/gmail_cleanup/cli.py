"""
gmail-cleanup — AI-powered (or heuristic) Gmail inbox cleanup CLI.

Usage:
  gmail-cleanup plan.json              # dry-run a plan (count only)
  gmail-cleanup plan.json --execute    # execute the plan (trash messages)
  gmail-cleanup plan.json --execute --limit 500
  cat plan.json | gmail-cleanup -      # read plan from stdin
  gmail-cleanup --undo                 # restore messages from last run
  gmail-cleanup --auto                 # print aggressive heuristic plan as JSON
  gmail-cleanup --auto --execute       # generate and immediately execute heuristic plan
  gmail-cleanup --auto --execute --limit N

  --dry-run is a deprecated alias for the default (no-execute) mode.

Plan format (plan.json):
{
  "queries": [
    {"name": "All Promotions", "query": "category:promotions"},
    {"name": "Old GitHub",     "query": "before:2026/2/6 from:github.com"}
  ]
}
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Optional, Union

from googleapiclient.discovery import build

from .auth import authenticate
from .gmail_ops import batch_restore, batch_trash, get_all_message_ids
from .heuristics import generate_aggressive_plan
from .history import append_history, read_last_history_entry


# ---------------------------------------------------------------------------
# Internal plan runner
# ---------------------------------------------------------------------------


def _run_plan(plan: dict, execute: bool, limit: Optional[int]) -> None:
    """Execute (or dry-run) a plan dict against the Gmail API."""
    queries = plan.get("queries", [])
    if not queries:
        print("No queries in plan. Nothing to do.")
        sys.exit(0)

    if not execute:
        print("DRY RUN — counting only, no emails will be deleted.\n")

    print("Authenticating...")
    creds = authenticate()
    service = build("gmail", "v1", credentials=creds)

    grand_total = 0
    all_ids_by_query = {}

    for entry in queries:
        name = entry.get("name", "Unnamed")
        query = entry["query"]
        print(f"\n[{name}]")
        ids = get_all_message_ids(service, query)

        if limit is not None and len(ids) > limit:
            ids = ids[:limit]

        if not ids:
            print("  0 messages — skipping.")
            continue

        if execute:
            print(f"  Found {len(ids)} — trashing...")
            batch_trash(service, ids)
            all_ids_by_query[name] = ids
        else:
            print(f"  Would trash {len(ids)} messages.")

        grand_total += len(ids)

    print(f"\n{'=' * 50}")
    if execute:
        print(f"Done. Total trashed: {grand_total}")
        print("Gmail -> Trash -> Empty Trash to free space immediately.")
        if all_ids_by_query:
            flat_ids = [mid for ids in all_ids_by_query.values() for mid in ids]
            append_history({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "queries": plan.get("queries", []),
                "trashed_ids": flat_ids,
                "count": len(flat_ids),
            })
            print("Run `gmail-cleanup --undo` to restore if needed.")
    else:
        print(f"Dry run complete. Would trash: {grand_total}")


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------


def cmd_run(
    plan_arg: Union[str, dict],
    execute: bool,
    limit: Optional[int],
) -> None:
    """Load a plan from a file path, '-' for stdin, or a pre-loaded dict, then run it."""
    if isinstance(plan_arg, dict):
        plan = plan_arg
    elif plan_arg == "-":
        plan = json.load(sys.stdin)
    else:
        with open(plan_arg) as f:
            plan = json.load(f)

    _run_plan(plan, execute=execute, limit=limit)


def cmd_undo() -> None:
    """Restore messages trashed in the most recent run."""
    entry = read_last_history_entry()
    if not entry:
        print("No cleanup history found. Nothing to undo.")
        sys.exit(1)

    all_ids = entry.get("trashed_ids", [])
    if not all_ids:
        print("Last history entry has no trashed message IDs.")
        sys.exit(1)
    print("Authenticating...")
    creds = authenticate()
    service = build("gmail", "v1", credentials=creds)

    print(f"Restoring {len(all_ids)} messages from Trash...")
    batch_restore(service, all_ids)
    print(f"Done. {len(all_ids)} messages restored to Inbox.")


def cmd_auto(execute: bool, limit: Optional[int]) -> None:
    """Generate aggressive heuristic plan; optionally execute it."""
    plan = generate_aggressive_plan()

    if not execute:
        # Print plan to stdout for piping / review
        print(
            "# Generated aggressive cleanup plan. Pipe to --execute to run it,"
            " or save and edit first.",
            file=sys.stderr,
        )
        print(json.dumps(plan, indent=2))
        return

    # execute path
    _run_plan(plan, execute=True, limit=limit)


# ---------------------------------------------------------------------------
# Argument parsing & dispatch
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gmail-cleanup",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "plan",
        nargs="?",
        metavar="PLAN",
        help="Path to a JSON plan file, or '-' to read from stdin.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        default=False,
        help="Actually trash matching messages (default: dry-run / count only).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        dest="dry_run",
        help="[Deprecated] No-op flag — dry-run is already the default without --execute.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Cap the number of messages processed per query.",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        default=False,
        help="Restore messages trashed in the most recent run.",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        default=False,
        help=(
            "Generate an aggressive heuristic cleanup plan (no Claude required). "
            "Without --execute, prints the plan JSON to stdout. "
            "With --execute, runs the plan immediately."
        ),
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    # --- Validation ---

    if args.auto and args.undo:
        parser.error(
            "--undo does not take --auto. "
            "Run `gmail-cleanup --undo` to restore the most recent run."
        )

    if args.dry_run:
        print(
            "Warning: --dry-run is deprecated. Dry-run is the default when --execute is not passed.",
            file=sys.stderr,
        )

    # --- Dispatch ---

    if args.undo:
        if args.plan:
            parser.error("--undo does not accept a plan argument.")
        cmd_undo()
        return

    if args.auto:
        cmd_auto(execute=args.execute, limit=args.limit)
        return

    # Normal plan-file mode
    if not args.plan:
        parser.print_help()
        sys.exit(1)

    cmd_run(plan_arg=args.plan, execute=args.execute, limit=args.limit)
