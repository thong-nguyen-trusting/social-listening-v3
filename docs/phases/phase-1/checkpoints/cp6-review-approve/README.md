# CP6 — Review & Approve

**Code:** cp6-review-approve
**Order:** 6
**Depends On:** cp5-plan-generation
**Estimated Effort:** 1.5 ngay

## Muc tieu

Implement US-03a: user review plan, chon/bo chon steps, approve → tao ApprovalGrant record. Health gate ngan approve write actions khi account khong HEALTHY.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| backend/app/services/approval.py | created | ApprovalService: issue_grant(), validate_grant(), invalidate on plan edit |
| backend/app/api/plans.py | modified | Them POST /api/plans/{id}/approve |
| backend/app/schemas/plans.py | modified | Them ApprovalRequest, ApprovalGrantResponse |
| frontend/src/pages/ApprovePage.tsx | created | Plan review checklist + approve button + health gate |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | POST /api/plans/{id}/approve tao ApprovalGrant voi grant_id, approved_step_ids, plan_version | yes |
| CHECK-02 | Approve khi health != HEALTHY va co write steps → 400 error | yes |
| CHECK-03 | Approve voi 0 steps selected → 400 "Chon it nhat mot buoc" | yes |
| CHECK-04 | Edit plan sau khi approve → grant bi invalidated | yes |
| CHECK-05 | ApprovalGrant record trong DB co approver_id, approved_at, plan_version | yes |
| CHECK-06 | ApprovePage hien thi checklist voi write actions highlighted | no |
| CHECK-07 | Uncheck step co dependency → system warns ve dependency break | no |
