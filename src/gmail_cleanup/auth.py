"""
Gmail OAuth authentication.

credentials.json and token.pickle are resolved from os.getcwd() so that
pipx-installed users can store them in any project directory alongside
their cleanup plans.
"""

import os
import pickle
import sys
from typing import Any

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def _credentials_path() -> str:
    """Return path to credentials.json in the current working directory."""
    return os.path.join(os.getcwd(), "credentials.json")


def _token_path() -> str:
    """Return path to token.pickle in the current working directory."""
    return os.path.join(os.getcwd(), "token.pickle")


def _diagnose_http_error(e: HttpError) -> str:
    """Return a human-readable diagnosis for common HttpError codes."""
    status = e.resp.status if hasattr(e, "resp") else None
    if status == 401:
        return "401 Unauthorized — token may be revoked. Delete token.pickle and re-auth."
    if status == 403:
        return "403 Forbidden — check Gmail API is enabled and scopes are correct."
    if status == 429:
        return "429 Too Many Requests — Gmail rate limit hit. Wait and retry."
    return f"HTTP {status}: {e}"


def authenticate() -> Any:
    """Authenticate with Gmail API and return credentials.

    Looks for token.pickle and credentials.json in os.getcwd().
    On first run, opens a browser OAuth flow and writes token.pickle.
    """
    creds = None
    token_path = _token_path()
    creds_path = _credentials_path()

    if os.path.exists(token_path):
        with open(token_path, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except HttpError as e:
                print(f"ERROR refreshing token: {_diagnose_http_error(e)}")
                sys.exit(1)
        else:
            if not os.path.exists(creds_path):
                print("ERROR: credentials.json not found.")
                print(f"  Expected at: {creds_path}")
                print("  Run: bash setup.sh  (or /gmail-cleanup in Claude Code)")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)

    return creds
