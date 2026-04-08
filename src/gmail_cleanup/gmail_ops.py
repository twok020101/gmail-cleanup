"""
Gmail API operations: listing, trashing, and restoring messages.
"""

from typing import Any, List


SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

_BATCH_SIZE = 1000


def get_all_message_ids(service: Any, query: str) -> List[str]:
    """Return all message IDs matching the given Gmail search query."""
    ids = []
    page_token = None
    while True:
        result = (
            service.users()
            .messages()
            .list(userId="me", q=query, pageToken=page_token, maxResults=500)
            .execute()
        )
        ids.extend(m["id"] for m in result.get("messages", []))
        page_token = result.get("nextPageToken")
        if not page_token:
            break
    return ids


def batch_trash(service: Any, message_ids: List[str]) -> None:
    """Move a list of message IDs to Trash in batches."""
    total = len(message_ids)
    for i in range(0, total, _BATCH_SIZE):
        chunk = message_ids[i : i + _BATCH_SIZE]
        service.users().messages().batchModify(
            userId="me",
            body={
                "ids": chunk,
                "addLabelIds": ["TRASH"],
                "removeLabelIds": ["INBOX", "UNREAD"],
            },
        ).execute()
        print(f"    {min(i + _BATCH_SIZE, total)}/{total} trashed")


def batch_restore(service: Any, message_ids: List[str]) -> None:
    """Restore a list of message IDs from Trash back to Inbox in batches."""
    total = len(message_ids)
    for i in range(0, total, _BATCH_SIZE):
        chunk = message_ids[i : i + _BATCH_SIZE]
        service.users().messages().batchModify(
            userId="me",
            body={
                "ids": chunk,
                "removeLabelIds": ["TRASH"],
                "addLabelIds": ["INBOX"],
            },
        ).execute()
        print(f"    {min(i + _BATCH_SIZE, total)}/{total} restored")
