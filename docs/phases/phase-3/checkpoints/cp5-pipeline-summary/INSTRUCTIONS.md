# CP5 — Pipeline Summary API

**Mục tiêu:** Aggregate pipeline data into run response for frontend dashboard.
**Requires:** CP1-CP4 PASS — all interceptors storing data in checkpoints

---

## Bước 1 — Implement `build_pipeline_summary()`

File: `backend/app/services/pipeline_intelligence.py`

Reads checkpoint data from step runs, assembles:

```python
def build_pipeline_summary(self, step_checkpoints: dict[str, dict]) -> dict | None:
    if not self._enabled:
        return None
    summary = {}
    for step_id, cp in step_checkpoints.items():
        if cp.get("label_summary"):
            summary["heuristic_labeling"] = cp["label_summary"]
        if cp.get("group_scoring"):
            gs = cp["group_scoring"]
            summary["group_scoring"] = {
                "total": gs.get("total_groups", 0),
                "relevant": gs.get("relevant_groups", 0),
                "skipped": gs.get("skipped_groups", 0),
            }
        # ... similar for tier_counts, group_quality, etc.
    return summary or None
```

## Bước 2 — Runner: enrich get_run()

In `RunnerService.get_run()`, after building steps list:

```python
if self._pipeline_intel:
    step_checkpoints = {s["step_id"]: s.get("checkpoint", {}) for s in steps}
    pipeline_summary = self._pipeline_intel.build_pipeline_summary(step_checkpoints)
else:
    pipeline_summary = None
# Add to return dict
result["pipeline_summary"] = pipeline_summary
```

## Bước 3 — Schema update

If `backend/app/schemas/runs.py` has a RunResponse model, add:
```python
pipeline_summary: dict | None = None
```

## Bước 4 — Verify + result.json

```bash
uv run python docs/phases/phase-3/checkpoints/notify.py \
    --cp cp5-pipeline-summary --role implementer --status READY \
    --summary "Pipeline summary API on GET /api/runs/{run_id}" \
    --result-file docs/phases/phase-3/checkpoints/cp5-pipeline-summary/result.json

python3 docs/phases/phase-3/checkpoints/post-status.py \
    --result-file docs/phases/phase-3/checkpoints/cp5-pipeline-summary/result.json
```
