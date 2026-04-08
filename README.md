# gmail-cleanup

![License: MIT](https://img.shields.io/badge/license-MIT-green.svg) ![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg) ![Works with Claude Code](https://img.shields.io/badge/works%20with-Claude%20Code-8A2BE2.svg)

AI-powered Gmail cleanup that runs inside [Claude Code](https://claude.ai/code).

Claude reads your inbox, figures out what's junk, and deletes it — no manual filters, no dragging emails to trash one by one.

![demo](docs/demo.gif)

<sub>_Demo GIF is generated from [`docs/demo.tape`](docs/demo.tape) via [VHS](https://github.com/charmbracelet/vhs) — `brew install vhs && vhs docs/demo.tape`. The simulation is scripted ([`docs/demo.sh`](docs/demo.sh)) so no real Gmail account is needed to re-render it._</sub>

## How it works

```
Gmail MCP (read-only)     cleanup.py (delete access)
        │                         │
        ▼                         ▼
   Claude analyzes ──► generates plan ──► executes deletion
   your inbox           (JSON queries)     via Gmail API
```

1. Claude scans your inbox using the Gmail MCP (read-only)
2. Categorizes every sender: spam, newsletter, transactional, important
3. Shows you the plan and asks for confirmation
4. Runs `cleanup.py` which trashes matching emails via Gmail API

## Requirements

- [Claude Code](https://claude.ai/code) (CLI, desktop app, or IDE extension)
- Python 3.9+ ([python.org/downloads](https://www.python.org/downloads/))
- A Google account

### Platform support

| Platform | Status |
|---|---|
| macOS | Tested |
| Linux (Ubuntu, Fedora, etc.) | Supported |
| Windows (Git Bash / WSL) | Supported |
| Windows (PowerShell) | Supported via manual setup |

## Setup (one-time, ~5 min)

### 1. Clone this repo

```bash
git clone https://github.com/YOUR_USER/gmail-cleanup.git
cd gmail-cleanup
```

### 2. Install Python (if not already installed)

**macOS:**
```bash
brew install python
```

**Ubuntu/Debian:**
```bash
sudo apt install python3 python3-venv python3-pip
```

**Fedora:**
```bash
sudo dnf install python3
```

**Windows:**
Download from [python.org/downloads](https://www.python.org/downloads/) and check "Add to PATH" during install.

### 3. Open in Claude Code and run `/gmail-cleanup`

```bash
claude
```

Then type `/gmail-cleanup`. Claude walks you through everything:

1. **Gmail MCP** — Claude checks if it's connected, tells you how to add it if not
2. **Python setup** — runs `bash setup.sh` automatically (creates venv, installs deps)
3. **Google credentials** — Claude walks you through creating `credentials.json` step-by-step (one-time, ~3 min)
4. **First auth** — script opens your browser for Google login, approve once, token is cached

> **Why do I need credentials.json?**
> The Gmail MCP gives Claude read-only access. To actually *delete* emails, the script needs `gmail.modify` permission via your own Google OAuth credentials. Google requires each user to authorize this themselves — there's no way around it. Your credentials stay on your machine and are gitignored. See [`credentials.json.example`](credentials.json.example) for the expected format.

### Manual setup (no Claude)

If you prefer to set up without Claude:

```bash
# Unix/macOS/Linux
bash setup.sh

# Windows (PowerShell)
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

Then follow the `credentials.json` instructions printed by setup.sh, or see the [Google Cloud setup guide](#google-cloud-credentials-guide) below.

## Usage

Open this folder in Claude Code and say:

```
clean up my gmail
```

Or run the skill directly:

```
/gmail-cleanup
```

Claude will:
- Scan your inbox
- Show a summary of what it found
- Ask what to keep/delete
- Execute the cleanup

### Manual usage (without Claude)

Write your own plan and run the script directly:

```json
{
  "queries": [
    {"name": "All Promotions", "query": "category:promotions"},
    {"name": "All Spam", "query": "in:spam"},
    {"name": "Old GitHub", "query": "before:2026/2/6 from:github.com"}
  ]
}
```

```bash
# Dry-run is the DEFAULT — shows what would be deleted, touches nothing
venv/bin/python cleanup.py plan.json

# Actually trash the matching messages
venv/bin/python cleanup.py plan.json --execute

# Cap deletions per run (useful for trying things out safely)
venv/bin/python cleanup.py plan.json --execute --limit 50

# Oops — restore everything from the most recent run
venv/bin/python cleanup.py --undo
```

On Windows, swap `venv/bin/python` for `venv\Scripts\python`.

## What gets deleted by default

| Category | Action |
|---|---|
| Promotions tab | Delete all |
| Updates tab | Delete all |
| Spam | Delete all |
| Newsletters in Primary | Delete (after user confirmation) |
| Job platform spam | Delete |
| Bank/payment alerts | Keep recent, delete older than X months |
| GitHub, Apple, Google | Keep recent, delete older than X months |
| Personal emails | Never deleted |

## FAQ

**Is it safe?**
Emails go to Trash, not permanently deleted. You have 30 days to recover anything from Gmail's Trash. On top of that: **dry-run is the default** — you must pass `--execute` to delete anything, and `--undo` restores the most recent run if you change your mind.

**Can Claude delete without asking?**
No. The skill always shows the cleanup plan and waits for your confirmation before executing.

**Does my data leave my machine?**
The Gmail MCP reads emails through Claude's MCP connection. The deletion script runs 100% locally using your own Google OAuth credentials. No data is sent to any third party.

**Can I run it periodically?**
Yes. Come back to this folder in Claude Code every 2 weeks and say "clean up my gmail". Claude re-scans and generates a fresh plan each time.

## Google Cloud credentials guide

<details>
<summary>Step-by-step with screenshots description</summary>

> **Heads up: the "unverified app" screen is expected.** The first time you authorize, Google will show a scary-looking "Google hasn't verified this app" warning. This is normal for personal OAuth clients — you created the app yourself, so of course Google hasn't verified it. Click **Advanced** → **Go to &lt;your app name&gt; (unsafe)** to continue. You're granting access to your *own* OAuth client, which only runs on your machine.

1. Go to [console.cloud.google.com](https://console.cloud.google.com/)
2. Create a new project (any name, e.g. "gmail-cleanup")
3. Search "Gmail API" in the top search bar → click **Enable**
4. Go to **APIs & Services → OAuth consent screen**
   - User Type: **External** → Create
   - Fill in app name and your email
   - Add scope: `https://www.googleapis.com/auth/gmail.modify`
   - Add your Gmail as a **Test User** → Save
5. Go to **APIs & Services → Credentials**
   - **Create Credentials → OAuth client ID**
   - Application type: **Desktop app**
   - Click **Create** → **Download JSON**
6. Rename the downloaded file to `credentials.json`
7. Move it into this project folder

</details>

## License

MIT
