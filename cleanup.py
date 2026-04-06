"""
Gmail Cleanup Engine
Accepts a JSON cleanup plan and trashes matching emails.

Usage:
  python cleanup.py plan.json              # execute plan
  python cleanup.py plan.json --dry-run    # count only, don't delete
  cat plan.json | python cleanup.py -      # read from stdin

Plan format (plan.json):
{
  "queries": [
    {"name": "All Promotions", "query": "category:promotions"},
    {"name": "Old GitHub",     "query": "before:2026/2/6 from:github.com"}
  ]
}
"""

import json
import os
import pickle
import sys
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def authenticate():
    creds = None
    token_path = os.path.join(SCRIPT_DIR, "token.pickle")
    creds_path = os.path.join(SCRIPT_DIR, "credentials.json")

    if os.path.exists(token_path):
        with open(token_path, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                print("ERROR: credentials.json not found.")
                print("Run: bash setup.sh  (or /gmail-cleanup in Claude Code)")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)
    return creds


def get_all_message_ids(service, query):
    ids = []
    page_token = None
    while True:
        result = service.users().messages().list(
            userId="me", q=query, pageToken=page_token, maxResults=500
        ).execute()
        ids.extend(m["id"] for m in result.get("messages", []))
        page_token = result.get("nextPageToken")
        if not page_token:
            break
    return ids


def batch_trash(service, message_ids):
    BATCH_SIZE = 1000
    total = len(message_ids)
    for i in range(0, total, BATCH_SIZE):
        chunk = message_ids[i: i + BATCH_SIZE]
        service.users().messages().batchModify(
            userId="me",
            body={"ids": chunk, "addLabelIds": ["TRASH"], "removeLabelIds": ["INBOX", "UNREAD"]},
        ).execute()
        print(f"    {min(i + BATCH_SIZE, total)}/{total} trashed")


def get_venv_python():
    """Find the venv Python, works on both Unix and Windows."""
    for path in ["venv/bin/python", "venv/Scripts/python.exe"]:
        full = os.path.join(SCRIPT_DIR, path)
        if os.path.exists(full):
            return full
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    dry_run = "--dry-run" in sys.argv
    plan_arg = [a for a in sys.argv[1:] if not a.startswith("--")][0]

    # Load plan
    if plan_arg == "-":
        plan = json.load(sys.stdin)
    else:
        with open(plan_arg) as f:
            plan = json.load(f)

    queries = plan.get("queries", [])
    if not queries:
        print("No queries in plan. Nothing to do.")
        sys.exit(0)

    if dry_run:
        print("DRY RUN — counting only, no emails will be deleted.\n")

    print("Authenticating...")
    creds = authenticate()
    service = build("gmail", "v1", credentials=creds)

    grand_total = 0
    for entry in queries:
        name = entry.get("name", "Unnamed")
        query = entry["query"]
        print(f"\n[{name}]")
        ids = get_all_message_ids(service, query)
        if not ids:
            print("  0 messages — skipping.")
            continue
        if dry_run:
            print(f"  Would trash {len(ids)} messages.")
        else:
            print(f"  Found {len(ids)} — trashing...")
            batch_trash(service, ids)
        grand_total += len(ids)

    print(f"\n{'=' * 50}")
    if dry_run:
        print(f"Dry run complete. Would trash: {grand_total}")
    else:
        print(f"Done. Total trashed: {grand_total}")
        print("Gmail -> Trash -> Empty Trash to free space immediately.")


if __name__ == "__main__":
    main()
