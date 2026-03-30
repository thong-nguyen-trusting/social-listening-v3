# CP6 — Pipeline Dashboard UI

**Mục tiêu:** Show pipeline funnel visualization in MonitorPage.
**Requires:** CP5 PASS — pipeline_summary available in run API response

---

## Bước 1 — Update MonitorPage types

Add `pipeline_summary` to RunData type:

```typescript
type RunData = {
  // ... existing fields
  pipeline_summary?: {
    search_posts?: { total: number };
    heuristic_labeling?: { high: number; medium: number; low: number };
    group_scoring?: { total: number; relevant: number; skipped: number };
    comment_crawl?: { from_high: number; from_medium: number; from_low: number };
    group_quality_gate?: { passed: number; skipped: number };
  } | null;
};
```

## Bước 2 — Add PipelineFunnel component

Inline in MonitorPage or separate component. Render when `run.pipeline_summary` exists:

```tsx
{run.pipeline_summary ? (
  <div className="pipeline-funnel">
    <p className="eyebrow">Pipeline Intelligence</p>
    {/* Stage bars for each funnel step */}
  </div>
) : null}
```

Each stage shows:
- Label (e.g. "Posts found")
- Count bar with color coding
- Breakdown detail

## Bước 3 — Add CSS

```css
.pipeline-funnel { margin-top: 16px; }
.funnel-stage { display: flex; align-items: center; gap: 10px; margin-top: 8px; }
.funnel-bar { height: 24px; border-radius: 4px; min-width: 20px; }
.funnel-bar-high { background: rgba(124, 214, 162, 0.6); }
.funnel-bar-medium { background: rgba(251, 191, 36, 0.5); }
.funnel-bar-low { background: rgba(255, 115, 115, 0.4); }
.funnel-bar-skipped { background: rgba(29, 40, 53, 0.15); }
```

## Bước 4 — Build + verify

```bash
cd frontend && npm run build
```

## Bước 5 — result.json

```bash
uv run python docs/phases/phase-3/checkpoints/notify.py \
    --cp cp6-pipeline-dashboard --role implementer --status READY \
    --summary "Pipeline funnel UI in MonitorPage" \
    --result-file docs/phases/phase-3/checkpoints/cp6-pipeline-dashboard/result.json

python3 docs/phases/phase-3/checkpoints/post-status.py \
    --result-file docs/phases/phase-3/checkpoints/cp6-pipeline-dashboard/result.json
```
