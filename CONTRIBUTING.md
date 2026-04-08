# Contributing

Thanks for your interest in improving gmail-cleanup.

## Local setup

Follow the [Setup section in the README](README.md#setup-one-time-5-min). You'll need Python 3.9+, a Google Cloud project with Gmail API enabled, and `credentials.json`.

## Running in dev

```bash
bash setup.sh               # one-time: venv + deps
venv/bin/python cleanup.py cleanup_plan.json            # dry-run (default)
venv/bin/python cleanup.py cleanup_plan.json --execute  # actually trash
venv/bin/python cleanup.py --undo                       # restore last run
```

Use a throwaway Google account or a test label query while iterating.

## Good first issues

Check the issue tracker for items labeled `good first issue`. Docs fixes, better error messages, and additional platform test coverage are all welcome.

## Code style

- Keep `cleanup.py` a single file — no package split.
- Prefer the standard library. New third-party dependencies need discussion in an issue first (the only current deps are the official Google API client libraries).
- Match the existing style: plain functions, early returns, minimal abstraction.
