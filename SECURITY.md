# Security

## OAuth scope rationale

This tool requests `https://www.googleapis.com/auth/gmail.modify`.

- **Why not `gmail.readonly`?** The tool needs to move messages to Trash, which is a write operation. Read-only cannot do that.
- **Why not full `mail.google.com`?** We deliberately avoid the broadest scope. `gmail.modify` excludes permanent deletion, sending mail, and account/settings changes — none of which this tool needs.

In practice, the tool only ever calls `users.messages.trash`. Trashed messages are recoverable from Gmail's Trash for 30 days.

## Local execution

- `credentials.json` (your OAuth client) and `token.pickle` (your cached access token) live on your machine only.
- Both are gitignored and never transmitted anywhere except directly to Google's OAuth endpoints.
- The deletion script runs 100% locally. No third-party server is involved.

## Revoking access

If you want to stop this tool from having access to your Gmail:

1. Visit https://myaccount.google.com/permissions and remove the app you created.
2. Delete `token.pickle` from this folder.
3. Optionally delete `credentials.json` as well.

Next run will fail auth until you re-authorize.

## Reporting vulnerabilities

If you find a security issue, please open a GitHub issue (for non-sensitive reports) or email the maintainer at kshitijkurandwad01@gmail.com for anything that shouldn't be public. Please do not disclose exploitable issues publicly before a fix is available.
