#!/usr/bin/env python3
"""
Checkpoint notification script.
Sends status to ntfy.sh after each CP implementation or validation.

Usage (Implementation Agent):
    python checkpoints/notify.py \\
        --cp cp0-environment \\
        --role implementer \\
        --status READY \\
        --summary "Phase 0 complete. Python 3.12, uv, docker all verified." \\
        --result-file checkpoints/cp0-environment/result.json

Usage (Validator Agent):
    python checkpoints/notify.py \\
        --cp cp0-environment \\
        --role validator \\
        --status PASS \\
        --summary "All 5 checks passed. Environment is clean and ready." \\
        --result-file checkpoints/cp0-environment/validation.json

Status values:
    implementer: READY | BLOCKED
    validator:   PASS | FAIL | PARTIAL
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.json"

def load_config() -> dict:
    """Load config from config.json or environment variables."""
    config = {"ntfy_topic": "", "ntfy_base": "https://ntfy.sh"}

    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            config.update(json.load(f))

    # Environment variables override config file
    if os.environ.get("NTFY_TOPIC"):
        config["ntfy_topic"] = os.environ["NTFY_TOPIC"]
    if os.environ.get("NTFY_BASE"):
        config["ntfy_base"] = os.environ["NTFY_BASE"]

    return config


# ── Notification ──────────────────────────────────────────────────────────────

STATUS_EMOJI = {
    "READY":   "✅",
    "BLOCKED": "🚫",
    "PASS":    "✅",
    "FAIL":    "❌",
    "PARTIAL": "⚠️",
}

STATUS_PRIORITY = {
    "READY":   "default",
    "BLOCKED": "high",
    "PASS":    "default",
    "FAIL":    "high",
    "PARTIAL": "default",
}


def send_ntfy(
    topic: str,
    base_url: str,
    title: str,
    message: str,
    priority: str = "default",
    tags: str = "",
) -> bool:
    url = f"{base_url.rstrip('/')}/{topic}"
    headers = {
        "Title": title.encode("utf-8"),
        "Priority": priority,
        "Content-Type": "text/plain; charset=utf-8",
    }
    if tags:
        headers["Tags"] = tags

    try:
        data = message.encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except urllib.error.URLError as e:
        print(f"  ✗ Failed to send to ntfy.sh: {e}", file=sys.stderr)
        return False


def notify(cp: str, role: str, status: str, summary: str, result_file: str, config: dict):
    if not config.get("ntfy_topic"):
        print(
            "\nERROR: ntfy_topic not configured.\n"
            "  Option 1: Set NTFY_TOPIC env var\n"
            "  Option 2: Edit checkpoints/config.json\n",
            file=sys.stderr,
        )
        sys.exit(1)

    emoji = STATUS_EMOJI.get(status, "ℹ️")
    role_label = "impl" if role == "implementer" else "validator"
    title = f"[SLv3] {cp} | {role_label} | {status} {emoji}"

    tags_map = {
        ("implementer", "READY"):   "white_check_mark,computer",
        ("implementer", "BLOCKED"): "no_entry,computer",
        ("validator",   "PASS"):    "white_check_mark,test_tube",
        ("validator",   "FAIL"):    "x,test_tube",
        ("validator",   "PARTIAL"): "warning,test_tube",
    }
    tags = tags_map.get((role, status), "information_source")

    message_lines = [
        summary,
        "",
        f"CP:          {cp}",
        f"Role:        {role_label}",
        f"Status:      {status} {emoji}",
        f"Result file: {result_file}",
        f"Time:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Dashboard: https://ntfy.sh/{config['ntfy_topic']}",
    ]
    message = "\n".join(message_lines)

    print(f"\nSending notification...")
    print(f"  Title:   {title}")
    print(f"  Topic:   {config['ntfy_topic']}")

    ok = send_ntfy(
        topic=config["ntfy_topic"],
        base_url=config["ntfy_base"],
        title=title,
        message=message,
        priority=STATUS_PRIORITY.get(status, "default"),
        tags=tags,
    )

    if ok:
        print(f"  ✓ Sent successfully")
        print(f"\nView at: https://ntfy.sh/{config['ntfy_topic']}")
    else:
        print(f"  ✗ Failed — check network or topic name", file=sys.stderr)
        sys.exit(1)


# ── Result writer ─────────────────────────────────────────────────────────────

def write_result_template(cp_dir: Path, role: str, status: str, summary: str) -> Path:
    """Write a minimal result/validation JSON if not already present."""
    filename = "result.json" if role == "implementer" else "validation.json"
    filepath = cp_dir / filename

    if filepath.exists():
        print(f"  (result file already exists: {filepath})")
        return filepath

    template = {
        "cp": cp_dir.name,
        "role": role,
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "artifacts": [],
        "issues": [],
        "notes": "",
    }
    if role == "validator":
        template["checks"] = []
        template["ready_for_next_cp"] = status == "PASS"

    filepath.write_text(json.dumps(template, indent=2, ensure_ascii=False) + "\n")
    print(f"  Written: {filepath}")
    return filepath


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Send checkpoint notification to ntfy.sh"
    )
    parser.add_argument(
        "--cp", required=True,
        help="Checkpoint name, e.g. cp0-environment"
    )
    parser.add_argument(
        "--role", required=True,
        choices=["implementer", "validator"],
        help="Who is sending this notification"
    )
    parser.add_argument(
        "--status", required=True,
        choices=["READY", "BLOCKED", "PASS", "FAIL", "PARTIAL"],
        help="Status: READY/BLOCKED for implementer, PASS/FAIL/PARTIAL for validator"
    )
    parser.add_argument(
        "--summary", required=True,
        help="Short summary (1-2 sentences)"
    )
    parser.add_argument(
        "--result-file", default="",
        help="Path to result.json or validation.json (auto-detected if not given)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print notification without sending"
    )
    args = parser.parse_args()

    config = load_config()

    cp_dir = SCRIPT_DIR / args.cp
    if not cp_dir.exists():
        print(f"ERROR: CP directory not found: {cp_dir}", file=sys.stderr)
        sys.exit(1)

    result_file = args.result_file
    if not result_file:
        fname = "result.json" if args.role == "implementer" else "validation.json"
        result_file = str(cp_dir / fname)

    if args.dry_run:
        print(f"[DRY RUN] Would send:")
        print(f"  CP:     {args.cp}")
        print(f"  Role:   {args.role}")
        print(f"  Status: {args.status}")
        print(f"  Summary: {args.summary}")
        print(f"  File:   {result_file}")
        return

    notify(
        cp=args.cp,
        role=args.role,
        status=args.status,
        summary=args.summary,
        result_file=result_file,
        config=config,
    )


if __name__ == "__main__":
    main()
