#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path


TERMINAL_STATUSES = {"DONE", "FAILED", "CANCELLED", "ERROR"}


def utc_now() -> datetime:
    return datetime.now(UTC)


def run_local(cmd: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        input=input_text,
        text=True,
        capture_output=True,
        check=True,
    )


def remote_python(ssh_target: str, container: str, code: str) -> str:
    result = run_local(["ssh", ssh_target, "docker", "exec", "-i", container, "python", "-"], input_text=code)
    return result.stdout


def remote_docker_logs(ssh_target: str, container: str, since_iso: str) -> str:
    result = run_local(["ssh", ssh_target, "docker", "logs", "--since", since_iso, container])
    return result.stdout + result.stderr


def fetch_snapshot(ssh_target: str, container: str, run_id: str) -> dict:
    code = f"""
import json
import sqlite3

run_id = {run_id!r}
conn = sqlite3.connect("/data/app.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

out = {{}}

cur.execute("SELECT * FROM plan_runs WHERE run_id = ?", (run_id,))
run_row = cur.fetchone()
out["run"] = dict(run_row) if run_row else None

if not run_row:
    print(json.dumps(out, ensure_ascii=False))
    raise SystemExit(0)

plan_id = run_row["plan_id"]

cur.execute(
    "SELECT * FROM step_runs WHERE run_id = ? ORDER BY COALESCE(started_at, '9999-12-31T23:59:59'), step_run_id",
    (run_id,),
)
out["step_runs"] = [dict(row) for row in cur.fetchall()]

cur.execute(
    "SELECT step_id, step_order, action_type, read_or_write, target, estimated_count, estimated_duration_sec, risk_level, dependency_step_ids "
    "FROM plan_steps WHERE plan_id = ? ORDER BY step_order, step_id",
    (plan_id,),
)
out["plan_steps"] = [dict(row) for row in cur.fetchall()]

cur.execute("SELECT context_id FROM plans WHERE plan_id = ?", (plan_id,))
context_row = cur.fetchone()
context_id = context_row["context_id"] if context_row else None
out["context_id"] = context_id

if context_id:
    cur.execute("SELECT * FROM product_contexts WHERE context_id = ?", (context_id,))
    row = cur.fetchone()
    out["context"] = dict(row) if row else None
else:
    out["context"] = None

    # Phase 7 operational summaries.
summary_queries = {{
    "crawled_by_status": (
        "SELECT record_type, COALESCE(pre_ai_status, 'NULL') AS pre_ai_status, COUNT(*) AS count "
        "FROM crawled_posts WHERE run_id = ? GROUP BY record_type, pre_ai_status "
        "ORDER BY record_type, pre_ai_status"
    ),
    "crawled_by_step": (
        "SELECT step_run_id, record_type, COALESCE(pre_ai_status, 'NULL') AS pre_ai_status, COUNT(*) AS count "
        "FROM crawled_posts WHERE run_id = ? GROUP BY step_run_id, record_type, pre_ai_status "
        "ORDER BY step_run_id, record_type, pre_ai_status"
    ),
    "crawled_by_query_family": (
        "SELECT COALESCE(query_family, 'NULL') AS query_family, COALESCE(pre_ai_status, 'NULL') AS pre_ai_status, COUNT(*) AS count "
        "FROM crawled_posts WHERE run_id = ? GROUP BY query_family, pre_ai_status ORDER BY query_family, pre_ai_status"
    ),
    "crawled_by_batch_decision": (
        "SELECT COALESCE(batch_decision, 'NULL') AS batch_decision, COUNT(*) AS count "
        "FROM crawled_posts WHERE run_id = ? GROUP BY batch_decision ORDER BY batch_decision"
    ),
    "labels_by_status": (
        "SELECT COALESCE(label_status, 'NULL') AS label_status, COUNT(*) AS count "
        "FROM crawled_posts WHERE run_id = ? GROUP BY label_status ORDER BY label_status"
    ),
    "providers": (
        "SELECT COALESCE(provider_used, 'NULL') AS provider_used, fallback_used, COUNT(*) AS count "
        "FROM crawled_posts WHERE run_id = ? GROUP BY provider_used, fallback_used ORDER BY provider_used, fallback_used"
    ),
    "top_records": (
        "SELECT post_id, record_type, pre_ai_status, pre_ai_score, query_family, source_type, batch_decision, source_url, parent_post_id "
        "FROM crawled_posts WHERE run_id = ? ORDER BY COALESCE(pre_ai_score, -1) DESC, post_id LIMIT 25"
    ),
}}

out["summaries"] = {{}}
for key, query in summary_queries.items():
    cur.execute(query, (run_id,))
    out["summaries"][key] = [dict(row) for row in cur.fetchall()]

print(json.dumps(out, ensure_ascii=False))
"""
    return json.loads(remote_python(ssh_target, container, code))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def append_text(path: Path, text: str) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)


def safe_json_loads(value: str | None) -> dict | list | None:
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def summarize_phase7(snapshot: dict) -> dict:
    run = snapshot.get("run") or {}
    step_runs = snapshot.get("step_runs") or []
    context = snapshot.get("context") or {}
    summaries = (snapshot.get("summaries") or {})
    top_records = summaries.get("top_records") or []

    phase7_flags = {
        "retrieval_profile_present": bool(context.get("retrieval_profile_json")),
        "pre_ai_status_present": any((row.get("pre_ai_status") or "NULL") != "NULL" for row in summaries.get("crawled_by_status", [])),
        "batch_decision_present": any((row.get("batch_decision") or "NULL") != "NULL" for row in summaries.get("crawled_by_batch_decision", [])),
        "comment_step_zero_after_no_accepts": False,
    }

    accepted_total = 0
    uncertain_total = 0
    rejected_total = 0
    for row in summaries.get("crawled_by_status", []):
        status = row.get("pre_ai_status")
        count = int(row.get("count") or 0)
        if status == "ACCEPTED":
            accepted_total += count
        elif status == "UNCERTAIN":
            uncertain_total += count
        elif status == "REJECTED":
            rejected_total += count

    by_action = {}
    for plan_step in snapshot.get("plan_steps") or []:
        by_action[plan_step["step_id"]] = plan_step["action_type"]

    completed_steps = []
    running_steps = []
    pending_steps = []
    failed_steps = []
    for step in step_runs:
        summary = {
            "step_id": step["step_id"],
            "action_type": by_action.get(step["step_id"]),
            "status": step["status"],
            "started_at": step.get("started_at"),
            "ended_at": step.get("ended_at"),
            "actual_count": step.get("actual_count"),
            "error_message": step.get("error_message"),
        }
        if step["status"] == "DONE":
            completed_steps.append(summary)
        elif step["status"] == "RUNNING":
            running_steps.append(summary)
        elif step["status"] == "PENDING":
            pending_steps.append(summary)
        elif step["status"] == "FAILED":
            failed_steps.append(summary)

    for step in step_runs:
        if by_action.get(step["step_id"]) != "CRAWL_COMMENTS":
            continue
        if step.get("actual_count") == 0 and accepted_total == 0:
            phase7_flags["comment_step_zero_after_no_accepts"] = True

    checkpoint_batch_summaries = []
    for step in step_runs:
        checkpoint = safe_json_loads(step.get("checkpoint") or step.get("checkpoint_json"))
        if not isinstance(checkpoint, dict):
            continue
        for batch in checkpoint.get("batch_summaries") or []:
            checkpoint_batch_summaries.append(batch)

    decision_counter = Counter(batch.get("decision") for batch in checkpoint_batch_summaries if batch.get("decision"))

    concerns: list[str] = []
    if accepted_total == 0:
        concerns.append("No ACCEPTED records so far; retrieval is spending budget mostly on REJECTED/UNCERTAIN candidates.")
    if uncertain_total > 0 and accepted_total == 0:
        concerns.append("UNCERTAIN records are present without any ACCEPTED records, which suggests thresholds or query quality may still be too weak for strict mode.")
    if decision_counter.get("continue", 0) > 0 and accepted_total == 0:
        concerns.append("Batch health continued at least one weak query path despite zero accepted records; query abandonment may still be too slow.")
    if running_steps:
        for step in running_steps:
            concerns.append(
                f"Step {step['step_id']} ({step['action_type']}) is still RUNNING, so the end-to-end AI/theme stages have not been proven yet."
            )
    for step in failed_steps:
        if step.get("error_message"):
            concerns.append(
                f"Step {step['step_id']} is marked FAILED with error `{step['error_message']}`."
            )

    failure_mode = None
    if failed_steps:
        if any(step.get("error_message") == "run has no crawled posts" for step in failed_steps) and accepted_total == 0:
            failure_mode = (
                "post_run_labeling_failed_on_zero_eligible_records"
            )
            concerns.append(
                "The run failed after retrieval because auto-labeling still started in strict mode even though zero eligible ACCEPTED records were available."
            )

    recommendations = [
        "Tighten query abandonment when accepted_count stays at 0 after the first weak batch for strict-mode runs.",
        "Add adaptive query reformulation or fallback to better query families instead of continuing broad/merchant-heavy searches.",
        "Treat zero eligible records as a graceful terminal outcome for labeling/theme stages instead of failing the whole run.",
        "Persist richer run-level audit events so production analysis does not depend on large checkpoint blobs and container logs.",
        "Capture source/group quality memory to suppress repeatedly low-yield groups in later steps and future runs.",
        "Add completion SLA alerts for long-running retrieval steps so operators can detect stalls before morning review.",
    ]

    next_phase_options = [
        "Adaptive retrieval planner: use early batch outcomes to skip, rewrite, or reorder later query families.",
        "Source quality memory: maintain per-group and per-query quality scores across runs for smarter exploration budgets.",
        "Operator feedback loop: let users mark retrieved posts/groups as relevant or noisy to improve future gating.",
        "Run observability layer: timeline events, per-step counters, and provider traces exposed directly in UI/API.",
        "Goal-aware execution: stop the run early when enough high-confidence signals exist for the user question instead of always exhausting the plan.",
    ]

    return {
        "run_status": run.get("status"),
        "completion_reason": run.get("completion_reason"),
        "total_records": run.get("total_records"),
        "accepted_total": accepted_total,
        "uncertain_total": uncertain_total,
        "rejected_total": rejected_total,
        "phase7_flags": phase7_flags,
        "completed_steps": completed_steps,
        "running_steps": running_steps,
        "pending_steps": pending_steps,
        "failed_steps": failed_steps,
        "failure_mode": failure_mode,
        "batch_decisions": dict(decision_counter),
        "top_records": top_records[:10],
        "concerns": concerns,
        "recommendations": recommendations,
        "next_phase_options": next_phase_options,
    }


def render_report(snapshot: dict, analysis: dict, output_dir: Path) -> None:
    report_path = output_dir / "final_report.md"
    run = snapshot.get("run") or {}
    context = snapshot.get("context") or {}
    lines = [
        f"# Production Analysis For {run.get('run_id', 'unknown-run')}",
        "",
        "## Request Context",
        f"- Topic: {context.get('topic', 'N/A')}",
        f"- Run status: {analysis.get('run_status')}",
        f"- Completion reason: {analysis.get('completion_reason')}",
        f"- Started at: {run.get('started_at')}",
        f"- Ended at: {run.get('ended_at')}",
        f"- Total records persisted: {analysis.get('total_records')}",
        "",
        "## End-to-End Timeline",
    ]
    for item in analysis.get("completed_steps", []):
        lines.append(
            f"- DONE `{item['step_id']}` `{item['action_type']}` from {item.get('started_at')} to {item.get('ended_at')} "
            f"with actual_count={item.get('actual_count')}"
        )
    for item in analysis.get("running_steps", []):
        lines.append(
            f"- RUNNING `{item['step_id']}` `{item['action_type']}` since {item.get('started_at')}"
        )
    for item in analysis.get("failed_steps", []):
        lines.append(
            f"- FAILED `{item['step_id']}` `{item['action_type']}` from {item.get('started_at')} to {item.get('ended_at')} "
            f"with actual_count={item.get('actual_count')} error=`{item.get('error_message')}`"
        )
    for item in analysis.get("pending_steps", []):
        lines.append(f"- PENDING `{item['step_id']}` `{item['action_type']}`")

    flags = analysis.get("phase7_flags") or {}
    lines.extend(
        [
            "",
            "## Phase 7 Alignment",
            f"- Retrieval profile present: `{flags.get('retrieval_profile_present')}`",
            f"- Deterministic pre-AI statuses present: `{flags.get('pre_ai_status_present')}`",
            f"- Batch-level decisions present: `{flags.get('batch_decision_present')}`",
            f"- Selective comment expansion observed: `{flags.get('comment_step_zero_after_no_accepts')}`",
            f"- ACCEPTED / UNCERTAIN / REJECTED: `{analysis.get('accepted_total')}` / `{analysis.get('uncertain_total')}` / `{analysis.get('rejected_total')}`",
            "",
            "## Initial Verdict",
        ]
    )

    if flags.get("retrieval_profile_present") and flags.get("pre_ai_status_present") and flags.get("batch_decision_present"):
        lines.append("- Phase 7 logic is partially active in production: retrieval profile, deterministic gating, and batch health are visible in run artifacts.")
    else:
        lines.append("- Phase 7 logic is not fully observable from production artifacts yet.")

    if analysis.get("accepted_total", 0) == 0:
        lines.append("- The current run has not produced any ACCEPTED records yet, so business-value output is still weak even though gating is running.")
    if analysis.get("completion_reason") == "NO_ELIGIBLE_RECORDS":
        lines.append("- The run ended gracefully with zero eligible records after pre-AI gating, which matches the intended strict-mode behavior.")
    if analysis.get("failure_mode") == "post_run_labeling_failed_on_zero_eligible_records":
        lines.append("- The final FAILED state is misleading: the retrieval pipeline completed, but post-run auto-labeling treated zero eligible records as an exception instead of a graceful no-op.")
    if analysis.get("running_steps"):
        lines.append("- The run is still in progress, so this report is interim until final completion.")

    lines.extend(["", "## Efficiency Concerns"])
    for concern in analysis.get("concerns", []):
        lines.append(f"- {concern}")

    lines.extend(["", "## Recommended Fixes"])
    for recommendation in analysis.get("recommendations", []):
        lines.append(f"- {recommendation}")

    lines.extend(["", "## Next Phase Exploration"])
    for option in analysis.get("next_phase_options", []):
        lines.append(f"- {option}")

    lines.extend(["", "## Top Records Snapshot"])
    for record in analysis.get("top_records", []):
        lines.append(
            f"- `{record.get('post_id')}` status=`{record.get('pre_ai_status')}` score=`{record.get('pre_ai_score')}` "
            f"query_family=`{record.get('query_family')}` source_type=`{record.get('source_type')}`"
        )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_status(snapshot: dict, analysis: dict, output_dir: Path) -> None:
    status_path = output_dir / "status.md"
    run = snapshot.get("run") or {}
    lines = [
        f"# Live Status For {run.get('run_id', 'unknown-run')}",
        "",
        f"- Last updated (UTC): {utc_now().isoformat()}",
        f"- Run status: `{analysis.get('run_status')}`",
        f"- Completion reason: `{analysis.get('completion_reason')}`",
        f"- Total records: `{analysis.get('total_records')}`",
        f"- ACCEPTED / UNCERTAIN / REJECTED: `{analysis.get('accepted_total')}` / `{analysis.get('uncertain_total')}` / `{analysis.get('rejected_total')}`",
        f"- Batch decisions: `{json.dumps(analysis.get('batch_decisions') or {}, ensure_ascii=False)}`",
        "",
        "## Running Steps",
    ]
    running_steps = analysis.get("running_steps") or []
    if running_steps:
        for step in running_steps:
            lines.append(f"- `{step['step_id']}` `{step['action_type']}` since {step.get('started_at')}")
    else:
        lines.append("- None")
    status_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitor a production run on the ChiaseGPU VM.")
    parser.add_argument("run_id")
    parser.add_argument("--ssh-target", default="chiasegpu-vm")
    parser.add_argument("--container", default="social-listening-v3")
    parser.add_argument("--interval-sec", type=int, default=300)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--max-polls", type=int, default=0)
    args = parser.parse_args()

    output_dir = Path(args.output_dir).expanduser().resolve()
    snapshots_dir = output_dir / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    state_path = output_dir / "state.json"
    full_log_path = output_dir / "full.log"
    monitor_log_path = output_dir / "monitor.log"
    latest_snapshot_path = output_dir / "latest_snapshot.json"
    latest_analysis_path = output_dir / "latest_analysis.json"

    state = {}
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))

    poll_count = 0
    while True:
        poll_started_at = utc_now()
        try:
            snapshot = fetch_snapshot(args.ssh_target, args.container, args.run_id)
            if not snapshot.get("run"):
                raise RuntimeError(f"Run {args.run_id} was not found on production.")

            run_started = datetime.fromisoformat(snapshot["run"]["started_at"])
            if run_started.tzinfo is None:
                run_started = run_started.replace(tzinfo=UTC)

            since_iso = state.get("last_log_since") or (run_started - timedelta(seconds=30)).isoformat().replace("+00:00", "Z")
            log_chunk = remote_docker_logs(args.ssh_target, args.container, since_iso)
            if log_chunk:
                append_text(full_log_path, f"\n\n===== poll {poll_started_at.isoformat()} =====\n")
                append_text(full_log_path, log_chunk)

            analysis = summarize_phase7(snapshot)

            snapshot_name = poll_started_at.strftime("%Y%m%dT%H%M%SZ")
            write_json(snapshots_dir / f"{snapshot_name}.json", snapshot)
            write_json(latest_snapshot_path, snapshot)
            write_json(latest_analysis_path, analysis)
            update_status(snapshot, analysis, output_dir)
            render_report(snapshot, analysis, output_dir)

            state = {
                "run_id": args.run_id,
                "last_polled_at": poll_started_at.isoformat(),
                "last_log_since": poll_started_at.isoformat().replace("+00:00", "Z"),
                "run_status": analysis.get("run_status"),
            }
            write_json(state_path, state)
            poll_count += 1

            append_text(
                monitor_log_path,
                f"[{poll_started_at.isoformat()}] status={analysis.get('run_status')} "
                f"records={analysis.get('total_records')} accepted={analysis.get('accepted_total')} "
                f"uncertain={analysis.get('uncertain_total')} rejected={analysis.get('rejected_total')}\n",
            )

            if (analysis.get("run_status") or "").upper() in TERMINAL_STATUSES:
                append_text(monitor_log_path, f"[{utc_now().isoformat()}] terminal status reached, monitor exiting\n")
                return 0
            if args.max_polls and poll_count >= args.max_polls:
                append_text(monitor_log_path, f"[{utc_now().isoformat()}] max polls reached, monitor exiting\n")
                return 0
        except Exception as exc:  # noqa: BLE001
            append_text(monitor_log_path, f"[{poll_started_at.isoformat()}] ERROR {exc}\n")

        time.sleep(max(30, args.interval_sec))


if __name__ == "__main__":
    sys.exit(main())
