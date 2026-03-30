# CP6 — Review & Approve

**Muc tieu:** ApprovalService + health-gated approval flow + grant invalidation.
**Requires:** CP5 PASS (plan co steps de approve)

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp6-review-approve/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau implement CP6 — Review & Approve",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

## Buoc 1 — ApprovalService

Tao `backend/app/services/approval.py`:

```python
class ApprovalService:
    async def issue_grant(self, plan_id: str, approved_step_ids: list[str]) -> ApprovalGrant:
        plan = await repo.get_plan(plan_id)

        # Health gate: neu co write steps va health != HEALTHY → reject
        write_steps = [s for s in plan.steps if s.step_id in approved_step_ids and s.read_or_write == 'WRITE']
        if write_steps and not health_monitor.is_write_allowed():
            raise HealthGateException("Account not HEALTHY — write actions blocked")

        if not approved_step_ids:
            raise ValidationException("Chon it nhat mot buoc")

        grant = ApprovalGrant(
            grant_id=generate_id(),
            plan_id=plan_id,
            plan_version=plan.version,
            approved_step_ids=json.dumps(approved_step_ids),
            approver_id='local_user',
        )
        await repo.save_grant(grant)
        return grant

    async def validate_grant(self, grant_id: str, plan_id: str) -> bool:
        grant = await repo.get_grant(grant_id)
        plan = await repo.get_plan(plan_id)
        return grant and not grant.invalidated and grant.plan_version == plan.version
```

Grant invalidation — khi plan bi edit:
```python
def invalidate_grant_if_needed(plan_id: str, new_version: int):
    grant = repo.get_valid_grant(plan_id)
    if grant and grant.plan_version != new_version:
        repo.invalidate_grant(grant.grant_id, reason="plan_edited_after_approval")
```

Wire vao PlannerService.refine_plan() (CP5).

## Buoc 2 — Approve API

Update `backend/app/api/plans.py`:
- `POST /api/plans/{plan_id}/approve` — body: {step_ids: string[]}
- 400 neu health gate fail
- 400 neu 0 steps
- 200 → ApprovalGrantResponse

## Buoc 3 — Frontend ApprovePage

Tao `frontend/src/pages/ApprovePage.tsx`:
- Load plan steps dang checklist (checkbox per step)
- Write actions: canh bao icon, background mau do nhat
- HealthBadge hien thi o goc — neu khong HEALTHY, disable approve button
- Uncheck step → check dependency warnings
- Button "Approve and Run" → POST approve → navigate to MonitorPage (CP7)

## Buoc 4 — Viet result.json va gui notification

```json
{
  "cp": "cp6-review-approve",
  "role": "implementer",
  "status": "READY",
  "timestamp": "<ISO8601>",
  "summary": "Approval flow with health gate, grant invalidation on plan edit.",
  "artifacts": [
    {"file": "backend/app/services/approval.py", "action": "created"},
    {"file": "backend/app/api/plans.py", "action": "modified"},
    {"file": "frontend/src/pages/ApprovePage.tsx", "action": "created"}
  ],
  "issues": [],
  "notes": ""
}
```

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp6-review-approve \
    --role implementer \
    --status READY \
    --summary "Approval flow complete." \
    --result-file docs/phases/phase-1/checkpoints/cp6-review-approve/result.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp6-review-approve/result.json
```
