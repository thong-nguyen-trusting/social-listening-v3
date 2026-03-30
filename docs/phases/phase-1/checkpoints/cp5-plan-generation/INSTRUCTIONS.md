# CP5 — Plan Generation

**Muc tieu:** AI tao research plan tu keywords → ordered steps voi versioning va NL refinement.
**Requires:** CP4 PASS (ProductContext voi keywords_ready)

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp5-plan-generation/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau implement CP5 — Plan Generation",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

## Buoc 1 — Plan generation skill prompt

Tao `backend/app/skills/plan_generation.md`:
- Input: ProductContext (topic + keywords)
- Output: ordered list of PlanSteps
- Rules:
  - CRAWL_FEED la READ, risk=LOW
  - JOIN_GROUP la WRITE, risk=HIGH
  - Moi step co dependency_step_ids
  - Estimate count va duration cho moi step
  - Warnings neu topic co van de (qua rong, private groups only, etc.)

## Buoc 2 — PlannerService.generate_plan()

Update `backend/app/services/planner.py`:
```python
async def generate_plan(self, context_id: str) -> Plan:
    context = await repo.get_context(context_id)
    assert context.status == 'keywords_ready'

    response = await ai_client.call(
        model="claude-opus-4-6",
        system_prompt=PLAN_SKILL_PROMPT,
        user_input=json.dumps({"topic": context.topic, "keywords": context.keyword_json}),
        thinking=True,
        stream=True,
    )
    # Parse response → PlanStep list
    # Save Plan + PlanSteps to DB (version=1)
    ...

async def refine_plan(self, plan_id: str, instruction: str) -> Plan:
    # Load current plan
    # AI call voi current plan + user instruction
    # Save new version (version += 1)
    ...
```

## Buoc 3 — Plan API

Update `backend/app/api/plans.py`:
- `POST /api/plans` — body: {context_id} → generate_plan() → PlanResponse
- `PATCH /api/plans/{plan_id}` — body: {instruction} → refine_plan()
- `GET /api/plans/{plan_id}` — tra ve plan voi steps

## Buoc 4 — Frontend PlanPage

Tao `frontend/src/pages/PlanPage.tsx`:
- Hien thi plan steps dang table/list
- Write actions: icon canh bao, background mau do nhat, label "Write Action"
- Risk levels: LOW=xanh, MEDIUM=vang, HIGH=do
- Text input cho natural language refinement
- Button "Proceed to Review" → navigate to ApprovePage

## Buoc 5 — Viet result.json va gui notification

```json
{
  "cp": "cp5-plan-generation",
  "role": "implementer",
  "status": "READY",
  "timestamp": "<ISO8601>",
  "summary": "Plan generation with Opus 4.6. Versioning, NL refinement, write action classification.",
  "artifacts": [
    {"file": "backend/app/services/planner.py", "action": "modified"},
    {"file": "backend/app/skills/plan_generation.md", "action": "created"},
    {"file": "backend/app/api/plans.py", "action": "modified"},
    {"file": "frontend/src/pages/PlanPage.tsx", "action": "created"}
  ],
  "issues": [],
  "notes": ""
}
```

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp5-plan-generation \
    --role implementer \
    --status READY \
    --summary "Plan generation complete." \
    --result-file docs/phases/phase-1/checkpoints/cp5-plan-generation/result.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp5-plan-generation/result.json
```
