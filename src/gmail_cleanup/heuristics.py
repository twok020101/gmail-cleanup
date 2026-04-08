"""
Aggressive heuristic cleanup plan generator.

Pure Python — no google deps, no intra-package imports.
Safe to import standalone for piping / preview purposes.
"""


def generate_aggressive_plan() -> dict:
    """Return a cleanup plan dict matching the executor's expected format.

    Aggressive defaults — will delete a lot. Users must explicitly --execute
    and can --undo if they change their mind.

    Explicitly AVOIDS: label:starred, label:important, in:sent, in:drafts,
    category:personal, and anything matching a VIP sender (not yet configurable).
    """
    return {
        "queries": [
            {
                "name": "Promotions tab",
                "query": "category:promotions -label:starred -label:important",
            },
            {
                "name": "Social tab (older than 14d)",
                "query": "category:social older_than:14d -label:starred -label:important",
            },
            {
                "name": "Updates tab (older than 30d)",
                "query": "category:updates older_than:30d -label:starred -label:important",
            },
            {
                "name": "Spam",
                "query": "in:spam",
            },
            {
                "name": "No-reply senders older than 90d",
                "query": (
                    "(from:noreply OR from:no-reply OR from:donotreply OR from:do-not-reply)"
                    " older_than:90d -label:starred -label:important -category:personal"
                ),
            },
            {
                "name": "Job platform spam older than 60d",
                "query": (
                    "(from:linkedin.com OR from:indeed.com OR from:ziprecruiter.com"
                    " OR from:glassdoor.com OR from:wellfound.com OR from:angel.co)"
                    " older_than:60d -label:starred -label:important"
                ),
            },
            {
                "name": "Unsubscribe-containing older than 90d",
                "query": (
                    '"unsubscribe" older_than:90d -label:starred -label:important'
                    " -category:personal"
                ),
            },
        ]
    }
