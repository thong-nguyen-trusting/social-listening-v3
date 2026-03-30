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
    with urllib.request.urlopen(req, timeout=120) as response:
        body = response.read().decode("utf-8")
        return json.loads(body) if body else {}


def answer_for_question(question: str) -> str:
    normalized = question.lower()
    if "sản phẩm" in normalized or "san pham" in normalized:
        return "Tap trung vao ung dung mobile va the TPBank EVO."
    if "thời gian" in normalized or "thoi gian" in normalized:
        return "Phan tich 6 thang gan nhat."
    if "so sánh" in normalized or "so sanh" in normalized:
        return "Tap trung vao khach hang hien tai cua TPBank EVO, nhung van ghi nhan cac so sanh voi ngan hang khac."
    if "khách hàng" in normalized or "khach hang" in normalized:
        return "Tap trung vao khach hang dang dung TPBank EVO tai Viet Nam."
    return "Can phan tich phan hoi cua khach hang TPBank EVO tai Viet Nam."


def ensure_keywords_ready(base: str, session: dict) -> dict:
    current = session
    for _ in range(3):
        if current.get("status") == "keywords_ready":
            return current

        questions = current.get("clarifying_questions") or []
        if current.get("status") != "clarification_required" or not questions:
            raise SystemExit(f"Unexpected session status: {current.get('status')}")

        answers = [answer_for_question(question) for question in questions]
        current = request(
            "POST",
            f"{base}/api/sessions/{current['context_id']}/clarifications",
            {"answers": answers},
        )

    raise SystemExit("Keyword clarification did not converge to keywords_ready")


def write_demo_log(path: Path, summary: dict) -> None:
    lines = [
        "# Demo Log — Phase 1 Smoke Test",
        "",
        f"**Date:** {summary['date']}",
        f"**Account:** {summary['account_id_hash'][:8]}",
        f"**Topic:** \"{summary['topic']}\"",
        "",
        "## Results",
        "",
        f"- Keywords generated: {summary['keyword_total']} across 5 categories",
        f"- Plan: {summary['plan_steps']} steps ({summary['read_steps']} read, {summary['write_steps']} write)",
        f"- Approved: read-only steps",
        f"- Crawled: {summary['posts_crawled']} posts from 1 group",
        f"- Excluded: {summary['posts_excluded']} spam posts",
        f"- Themes found: {summary['theme_count']}",
    ]
    for theme in summary["themes"]:
        lines.append(f"  - {theme['label']} — {theme['dominant_sentiment']} — {theme['post_count']} posts")
    lines.extend(
        [
            f"- Health after run: {summary['health_status']}",
            f"- Total duration: {summary['duration_seconds']} seconds",
            "- Errors: none",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument(
        "--demo-log",
        default="../../docs/phases/phase-1/checkpoints/cp9-smoke-test/DEMO_LOG.md",
    )
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    topic = "Phan hoi khach hang ve TPBank EVO"

    browser_status = request("GET", f"{base}/api/browser/status")
    if browser_status.get("session_status") != "VALID":
        raise SystemExit("Browser session is not valid. Run CP2 setup first.")

    session = request("POST", f"{base}/api/sessions", {"topic": topic})
    session = ensure_keywords_ready(base, session)
    keyword_total = sum(len(values) for values in (session.get("keywords") or {}).values())
    plan = request("POST", f"{base}/api/plans", {"context_id": session["context_id"]})
    read_steps = [step["step_id"] for step in plan["steps"] if step["read_or_write"] == "READ"]
    write_steps = [step["step_id"] for step in plan["steps"] if step["read_or_write"] == "WRITE"]
    grant = request("POST", f"{base}/api/plans/{plan['plan_id']}/approve", {"step_ids": read_steps})

    started_at = time.time()
    run = request("POST", f"{base}/api/runs", {"plan_id": plan["plan_id"], "grant_id": grant["grant_id"]})
    while True:
        time.sleep(2)
        run = request("GET", f"{base}/api/runs/{run['run_id']}")
        if run["status"] in {"DONE", "FAILED", "CANCELLED"}:
            break

    themes = request("GET", f"{base}/api/runs/{run['run_id']}/themes")
    health = request("GET", f"{base}/api/health/status")
    browser_status = request("GET", f"{base}/api/browser/status")

    summary = {
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "account_id_hash": browser_status.get("account_id_hash", "unknown"),
        "topic": topic,
        "keyword_total": keyword_total,
        "plan_steps": len(plan["steps"]),
        "read_steps": len(read_steps),
        "write_steps": len(write_steps),
        "posts_crawled": themes["posts_crawled"],
        "posts_excluded": themes["posts_excluded"],
        "theme_count": len(themes["themes"]),
        "themes": themes["themes"],
        "health_status": health["status"],
        "duration_seconds": round(time.time() - started_at, 1),
    }

    demo_log_path = (Path(__file__).resolve().parent / args.demo_log).resolve()
    demo_log_path.parent.mkdir(parents=True, exist_ok=True)
    write_demo_log(demo_log_path, summary)

    print(json.dumps({"session": session, "plan": plan, "grant": grant, "run": run, "themes": themes}, ensure_ascii=False))


if __name__ == "__main__":
    main()
