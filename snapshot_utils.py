"""
snapshot_utils.py – Shared helpers for managing dated snapshot CSV files.

Snapshot files live in snapshots/ and are named snapshot-YYYY-MM-DD.csv.
"""

from __future__ import annotations

import base64
import os
import re
import requests
import pandas as pd
from datetime import datetime, timedelta

SNAPSHOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snapshots")
_FILENAME_RE = re.compile(r"^snapshot-(\d{4}-\d{2}-\d{2})\.csv$")


def get_latest_snapshot_date() -> datetime.date | None:
    """Return the date of the most recent snapshot file, or None if none exist."""
    if not os.path.isdir(SNAPSHOTS_DIR):
        return None
    dates = []
    for fname in os.listdir(SNAPSHOTS_DIR):
        m = _FILENAME_RE.match(fname)
        if m:
            dates.append(datetime.strptime(m.group(1), "%Y-%m-%d").date())
    return max(dates) if dates else None


def should_take_snapshot(months: int = 3) -> bool:
    """Return True if no snapshot exists within the last *months* months."""
    latest = get_latest_snapshot_date()
    if latest is None:
        return True
    cutoff = (datetime.now() - timedelta(days=months * 30)).date()
    return latest < cutoff


def repos_to_csv(repos: list[dict], path: str) -> int:
    """Write *repos* (GitHub API format) to *path* as a snapshot CSV.

    Returns the number of rows written.
    """
    rows = []
    for repo in repos:
        rows.append({
            "Name": repo["name"],
            "Stars⭐": repo["stargazers_count"],
            "Last Updated": repo["pushed_at"].split("T")[0],
            "First Commit": repo["created_at"].split("T")[0],
            "URL": repo["html_url"],
            "Forks": repo["forks"],
            "Issues": repo["open_issues"],
            "Language": repo.get("language") or "No language",
            "License": repo["license"]["name"] if repo.get("license") else "No license",
            "Description": repo.get("description") or "No description",
            "Topics": ",".join(repo.get("topics") or []),
        })
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8")
    return len(rows)


def auto_snapshot(repos: list[dict]) -> str | None:
    """Save a new snapshot when no snapshot exists in the last 3 months.

    Returns the path of the newly created file, or None if skipped.
    """
    if not should_take_snapshot():
        return None
    today = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(SNAPSHOTS_DIR, f"snapshot-{today}.csv")
    if os.path.exists(path):
        return None  # already taken today
    repos_to_csv(repos, path)
    return path


def commit_snapshot_to_github(
    local_path: str,
    token: str,
    repo: str = "jcabot/oss-lowcode-tools",
    branch: str = "main",
) -> tuple[bool, str | None]:
    """Commit the snapshot CSV at *local_path* to GitHub via the Contents API.

    Uses a personal access token with 'contents: write' permission.
    Returns (success, error_detail_or_None).
    """
    filename = os.path.basename(local_path)
    repo_path = f"snapshots/{filename}"
    url = f"https://api.github.com/repos/{repo}/contents/{repo_path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    with open(local_path, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode("ascii")

    # Fetch existing SHA if the file already exists (required for updates)
    existing = requests.get(url, headers=headers, params={"ref": branch})
    sha = existing.json().get("sha") if existing.status_code == 200 else None

    payload: dict = {
        "message": f"Add snapshot {filename}",
        "content": content_b64,
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha

    response = requests.put(url, headers=headers, json=payload)
    if response.status_code in (200, 201):
        return True, None
    try:
        err = response.json().get("message", response.text)
    except Exception:
        err = response.text
    return False, f"HTTP {response.status_code}: {err[:200]}"
