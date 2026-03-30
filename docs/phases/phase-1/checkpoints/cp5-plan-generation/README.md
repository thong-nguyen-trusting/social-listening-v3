# CP5 — Plan Generation

**Code:** cp5-plan-generation
**Order:** 5
**Depends On:** cp4-keyword-analysis
**Estimated Effort:** 2 ngay

## Muc tieu

Implement US-02: AI tao research plan tu keywords da confirm. Plan bao gom ordered steps voi action_type, read/write classification, risk level. User co the chinh sua plan bang ngon ngu tu nhien va plan duoc versioned.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| backend/app/services/planner.py | modified | Them generate_plan(), refine_plan() |
| backend/app/skills/plan_generation.md | created | Plan generation skill prompt |
| backend/app/api/plans.py | modified | Them POST /api/plans, PATCH /api/plans/{id}, GET /api/plans/{id} |
| backend/app/schemas/plans.py | modified | Them PlanResponse, PlanStepSchema |
| frontend/src/pages/PlanPage.tsx | created | Plan viewer voi write action highlights |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | POST /api/plans tra ve plan voi ordered steps, moi step co action_type, read_or_write, target, estimated_count, risk_level | yes |
| CHECK-02 | Write action steps (JOIN_GROUP) co read_or_write=WRITE va risk_level=HIGH | yes |
| CHECK-03 | PATCH /api/plans/{id} voi natural language instruction thay doi plan va tang version | yes |
| CHECK-04 | Plan duoc luu trong DB voi plan_id, version, steps | yes |
| CHECK-05 | GET /api/plans/{id} tra ve plan hien tai voi tat ca steps | yes |
| CHECK-06 | PlanPage hien thi steps voi write actions duoc highlight rieng biet | no |
| CHECK-07 | Plan steps co dependency_step_ids dung logic (CRAWL_FEED truoc khi phan tich) | no |
