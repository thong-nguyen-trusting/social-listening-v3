# CP4 — Keyword Analysis

**Muc tieu:** User nhap topic → AI tra ve keywords 5 nhom → luu ProductContext.
**Requires:** CP1 PASS (schema), CP3 PASS (health check before AI calls)

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp4-keyword-analysis/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau implement CP4 — Keyword Analysis",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

## Buoc 1 — AIClient

Tao `backend/app/infra/ai_client.py` theo architecture.md Section 9:

```python
import anthropic

class AIClient:
    def __init__(self):
        self._client = anthropic.AsyncAnthropic()

    async def call(self, model: str, system_prompt: str, user_input: str,
                   stream: bool = False, thinking: bool = False):
        messages_params = {
            "model": model,
            "max_tokens": 4096,
            "system": [{
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}
            }],
            "messages": [{"role": "user", "content": user_input}],
        }
        if thinking:
            messages_params["thinking"] = {
                "type": "enabled",
                "budget_tokens": 2048
            }
        return await self._client.messages.create(**messages_params)
```

## Buoc 2 — Keyword skill prompt

Tao `backend/app/skills/keyword_analysis.md`:
- System prompt cho Claude Opus 4.6
- Vietnamese NLP rules: dang co dau + khong dau, slang (ib minh nhe, ship khong, con hang khong)
- Output format: JSON voi 5 categories
- Clarification logic: neu topic qua rong → tra ve questions thay vi keywords

## Buoc 3 — PlannerService.analyze_topic()

Tao `backend/app/services/planner.py`:
```python
class PlannerService:
    async def analyze_topic(self, topic: str) -> dict:
        # Load keyword_analysis.md prompt
        # Call AIClient voi claude-opus-4-6 + thinking
        # Parse response → KeywordMap hoac ClarifyingQuestions
        # Create ProductContext in DB
        ...
```

## Buoc 4 — Session API

Tao `backend/app/api/plans.py`:
- `POST /api/sessions` — nhan topic, goi analyze_topic(), tra ve context_id + keywords/questions
- `PATCH /api/sessions/{context_id}/keywords` — update keywords, set status=keywords_ready

Tao schemas tuong ung.

## Buoc 5 — Frontend KeywordPage

Tao `frontend/src/pages/KeywordPage.tsx`:
- Text input cho topic
- Hien thi keywords grouped theo 5 categories
- Cho phep add/remove/edit tung keyword
- Button "Confirm Keywords" → PATCH API → navigate to PlanPage

## Buoc 6 — Viet result.json va gui notification

```json
{
  "cp": "cp4-keyword-analysis",
  "role": "implementer",
  "status": "READY",
  "timestamp": "<ISO8601>",
  "summary": "Keyword analysis with Opus 4.6. Vietnamese NLP, 5 categories, clarification flow.",
  "artifacts": [
    {"file": "backend/app/infra/ai_client.py", "action": "created"},
    {"file": "backend/app/services/planner.py", "action": "created"},
    {"file": "backend/app/skills/keyword_analysis.md", "action": "created"},
    {"file": "backend/app/api/plans.py", "action": "created"},
    {"file": "frontend/src/pages/KeywordPage.tsx", "action": "created"}
  ],
  "issues": [],
  "notes": "Requires ANTHROPIC_API_KEY in .env"
}
```

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp4-keyword-analysis \
    --role implementer \
    --status READY \
    --summary "Keyword analysis complete." \
    --result-file docs/phases/phase-1/checkpoints/cp4-keyword-analysis/result.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp4-keyword-analysis/result.json
```
