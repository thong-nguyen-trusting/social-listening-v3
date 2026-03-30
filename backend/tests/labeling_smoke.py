from __future__ import annotations

import argparse
import json
import time
import urllib.request
from pathlib import Path


def request(method: str, url: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=180) as response:
        body = response.read().decode("utf-8")
        return json.loads(body) if body else {}


def write_demo_log(path: Path, summary: dict) -> None:
    lines = [
        "# Demo Log — Phase 2 Labeling Smoke",
        "",
        f"**Date:** {summary['date']}",
        f"**Run ID:** {summary['run_id']}",
        f"**Label Job:** {summary['label_job_id']}",
        "",
        "## Labeling",
        "",
        f"- Taxonomy version: {summary['taxonomy_version']}",
        f"- Status: {summary['label_status']}",
        f"- Records labeled: {summary['records_labeled']}/{summary['records_total']}",
        f"- Fallback: {summary['records_fallback']}",
        f"- Failed: {summary['records_failed']}",
        f"- Role counts: {json.dumps(summary['counts_by_author_role'], ensure_ascii=False)}",
        "",
        "## Themes",
        "",
    ]
    for filter_name, payload in summary["themes"].items():
        lines.append(
            f"- {filter_name}: included {payload['posts_included']}/{payload['posts_crawled']}, "
            f"excluded {payload['excluded_by_label_count']}, themes {len(payload['themes'])}"
        )
    lines.extend(
        [
            "",
            "## Audit Sample",
            "",
        ]
    )
    for record in summary["audit_records"]:
        label = record.get("label") or {}
        lines.append(
            f"- {record['post_id']} [{record['record_type']}] -> "
            f"{label.get('author_role', 'none')} / {label.get('label_reason', 'n/a')}"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--run-id", required=True)
    parser.add_argument(
        "--demo-log",
        default="../../docs/phases/phase-2/checkpoints/cp8-audit-backfill-smoke/DEMO_LOG.md",
    )
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    summary = request("GET", f"{base}/api/runs/{args.run_id}/labels/summary")
    if summary["status"] == "NOT_STARTED":
        summary = request("POST", f"{base}/api/runs/{args.run_id}/labels/jobs")

    started_at = time.time()
    while summary["status"] not in {"DONE", "PARTIAL", "FAILED"}:
        time.sleep(2)
        summary = request("GET", f"{base}/api/runs/{args.run_id}/labels/summary")
        if time.time() - started_at > 180:
            raise SystemExit("Labeling smoke timed out")

    themes = {
        audience_filter: request(
            "GET",
            f"{base}/api/runs/{args.run_id}/themes?audience_filter={audience_filter}",
        )
        for audience_filter in ("end_user_only", "include_seller", "include_brand")
    }
    audit = request("GET", f"{base}/api/runs/{args.run_id}/records?label_filter=excluded&limit=3")

    log_payload = {
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "run_id": args.run_id,
        "label_job_id": summary["label_job_id"],
        "taxonomy_version": summary["taxonomy_version"],
        "label_status": summary["status"],
        "records_total": summary["records_total"],
        "records_labeled": summary["records_labeled"],
        "records_fallback": summary["records_fallback"],
        "records_failed": summary["records_failed"],
        "counts_by_author_role": summary["counts_by_author_role"],
        "themes": themes,
        "audit_records": audit["records"],
    }

    demo_log_path = (Path(__file__).resolve().parent / args.demo_log).resolve()
    demo_log_path.parent.mkdir(parents=True, exist_ok=True)
    write_demo_log(demo_log_path, log_payload)

    print(json.dumps({"summary": summary, "themes": themes, "audit": audit}, ensure_ascii=False))


if __name__ == "__main__":
    main()
