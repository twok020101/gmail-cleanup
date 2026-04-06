# Gmail Cleanup — Claude Code Project

## What this is
An AI-powered Gmail cleanup tool. Claude reads your inbox via the Gmail MCP, intelligently decides what to delete, and executes via a local Python script with Gmail API delete permissions.

## How to use
Run `/gmail-cleanup` in Claude Code. That's it.

## Requirements
1. **Gmail MCP connected** — Add the Gmail MCP server in Claude Code settings
2. **credentials.json** — Google Cloud OAuth credentials (one-time setup, run `bash setup.sh`)
3. **Python venv** — Auto-created by `setup.sh`

## Architecture
- Claude (via Gmail MCP) = reads and analyzes emails (read-only)
- `cleanup.py` = deletes emails via Gmail API (write access via OAuth)
- `.claude/commands/gmail-cleanup.md` = the skill that orchestrates both

## Files
- `cleanup.py` — Deletion engine. Accepts a JSON plan file, trashes matching emails.
- `setup.sh` — One-time setup: creates venv, installs deps, guides credentials setup.
- `cleanup_plan.json` — Generated per-run by Claude. Contains the queries to execute.
- `credentials.json` — Your Google OAuth credentials (gitignored, never committed).
- `token.pickle` — Cached auth token (gitignored).
