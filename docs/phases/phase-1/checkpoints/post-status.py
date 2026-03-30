#!/usr/bin/env python3
"""
Post checkpoint status to the dashboard API.

Reads result.json (implementer) or validation.json (validator) and POSTs
to POST /api/projects/:slug/checkpoints/:code/status.

Usage:
    python3 checkpoints/post-status.py \\
        --result-file checkpoints/cp1-project-api/result.json \\
        [--dashboard-url http://localhost:3000] \\
        [--project-slug my-project]

Config (checkpoints/config.json):
    {
      "dashboard_url": "http://localhost:3000",
      "project_slug":  "my-project"
    }

Environment overrides:
    DASHBOARD_URL=http://localhost:3000
    PROJECT_SLUG=my-project
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.json"


# ── Config ─────────────────────────────────────────────────────────────────────

def load_config() -> dict:
    config = {
        "dashboard_url": "http://localhost:3000",
        "project_slug": "",
    }
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            config.update(json.load(f))
    if os.environ.get("DASHBOARD_URL"):
        config["dashboard_url"] = os.environ["DASHBOARD_URL"]
    if os.environ.get("PROJECT_SLUG"):
        config["project_slug"] = os.environ["PROJECT_SLUG"]
    return config


# ── Payload builder ────────────────────────────────────────────────────────────

def build_payload(data: dict) -> dict:
    """Transform result.json / validation.json → API payload."""
    role = data.get("role", "implementer")
    raw_issues = data.get("issues", [])
    raw_artifacts = data.get("artifacts", [])

    normalized_artifacts = []
    for artifact in raw_artifacts:
        if not isinstance(artifact, dict):
            continue

        action = artifact.get("action", "modified")
        action_map = {
            "updated": "modified",
            "changed": "modified",
            "created": "created",
            "modified": "modified",
            "verified": "verified",
            "deleted": "deleted",
        }
        normalized_artifacts.append({
            **artifact,
            "action": action_map.get(action, "modified"),
        })

    normalized_issues = []
    for issue in raw_issues:
        if isinstance(issue, str):
            normalized_issues.append({
                "severity": "warning",
                "message": issue,
            })
            continue

        if not isinstance(issue, dict):
            normalized_issues.append({
                "severity": "warning",
                "message": str(issue),
            })
            continue

        severity = issue.get("severity")
        if severity not in {"blocker", "warning"}:
            severity = "warning"

        message = (
            issue.get("message")
            or issue.get("description")
            or issue.get("recommendation")
            or issue.get("type")
            or ""
        )

        prefix = issue.get("check")
        if prefix and not message.startswith(f"{prefix}:"):
            message = f"{prefix}: {message}"

        normalized_issues.append({
            "severity": severity,
            "message": message,
        })

    if role == "implementer":
        payload: dict = {
            "role": "implementer",
            "status": data.get("status", "READY"),
            "summary": data.get("summary", ""),
            "readyForNextTrigger": False,
            "artifacts": normalized_artifacts,
            "issues": normalized_issues,
        }
        if data.get("notes"):
            payload["notes"] = data["notes"]

    else:  # validator
        status = data.get("status", "PASS")
        # ready_for_next_cp in file → readyForNextTrigger in API
        ready = data.get("ready_for_next_cp", status in ("PASS", "PARTIAL"))
        next_cp = data.get("next_cp", "")

        payload = {
            "role": "validator",
            "status": status,
            "summary": data.get("summary", ""),
            "readyForNextTrigger": bool(ready),
            "checks": data.get("checks", []),
            "issues": normalized_issues,
        }
        if next_cp:
            payload["nextCp"] = next_cp
            payload["nextActionMessage"] = f"Trigger {next_cp} implementation."

    return payload


# ── HTTP ───────────────────────────────────────────────────────────────────────

def post_status(result_file: str, dashboard_url: str, project_slug: str) -> bool:
    path = Path(result_file)
    if not path.exists():
        print(f"✗ File not found: {result_file}", file=sys.stderr)
        return False

    data = json.loads(path.read_text(encoding="utf-8"))
    cp_code = data.get("cp", path.parent.name)
    payload = build_payload(data)

    if not project_slug:
        print(
            "✗ project_slug not configured.\n"
            "  Option 1: Set PROJECT_SLUG env var\n"
            "  Option 2: Add \"project_slug\" to checkpoints/config.json",
            file=sys.stderr,
        )
        return False

    url = f"{dashboard_url.rstrip('/')}/api/projects/{project_slug}/checkpoints/{cp_code}/status"
    print(f"→ POST {url}")

    try:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())

        if result.get("ok"):
            print(f"✓ Dashboard updated: {result.get('updatedStatus')} [{cp_code}]")
            if result.get("readyForNextTrigger") and result.get("nextCp"):
                print(f"  → Next CP ready: {result['nextCp']}")
            return True
        else:
            print(f"✗ API error: {result.get('error')}", file=sys.stderr)
            return False

    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"✗ HTTP {e.code}: {body}", file=sys.stderr)
        return False
    except urllib.error.URLError as e:
        # Dashboard not running — non-fatal, agent can continue
        print(f"⚠ Dashboard unreachable ({e.reason}) — bỏ qua, tiếp tục bình thường")
        return True
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        return False


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Post checkpoint status to dashboard API"
    )
    parser.add_argument(
        "--result-file", required=True,
        help="Path to result.json or validation.json",
    )
    parser.add_argument(
        "--dashboard-url", default="",
        help="Dashboard base URL (default: http://localhost:3000)",
    )
    parser.add_argument(
        "--project-slug", default="",
        help="Project slug on the dashboard",
    )
    args = parser.parse_args()

    config = load_config()
    dashboard_url = args.dashboard_url or config["dashboard_url"]
    project_slug  = args.project_slug  or config["project_slug"]

    ok = post_status(args.result_file, dashboard_url, project_slug)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
