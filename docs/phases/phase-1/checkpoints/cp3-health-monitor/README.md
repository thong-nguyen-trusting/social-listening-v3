# CP3 — Health Monitor

**Code:** cp3-health-monitor
**Order:** 3
**Depends On:** cp2-browser-session
**Estimated Effort:** 1.5 ngay

## Muc tieu

Implement HealthMonitorService: event-driven state machine (HEALTHY → CAUTION → BLOCKED), signal detection tu BrowserAgent response interceptor, safety stop mechanism. US-00 hoan thanh sau CP nay.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| backend/app/services/health_monitor.py | created | HealthMonitorService state machine, signal handler |
| backend/app/infra/event_bus.py | created | In-process asyncio EventBus |
| backend/app/api/health.py | created | GET /api/health/status, POST /api/health/acknowledge, POST /api/health/reset |
| backend/app/schemas/health.py | created | Pydantic schemas cho health API |
| backend/app/infra/browser_agent.py | modified | Them _on_route() signal emission, detect CAPTCHA/action-blocked |
| frontend/src/components/HealthBadge.tsx | created | Health status indicator component |
| backend/app/main.py | modified | Register health router, start monitor background task |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | GET /api/health/status tra ve status=HEALTHY khi khong co signal | yes |
| CHECK-02 | Khi CAPTCHA signal duoc emit → status chuyen sang BLOCKED, cooldown_until duoc set | yes |
| CHECK-03 | Khi action-blocked signal → status chuyen sang CAUTION | yes |
| CHECK-04 | account_health_log ghi lai moi transition voi signal_type va timestamp | yes |
| CHECK-05 | POST /api/health/reset chi thanh cong khi cooldown da het | yes |
| CHECK-06 | HealthBadge component hien thi dung 3 trang thai voi mau sac khac nhau | no |
| CHECK-07 | EventBus dispatch events — subscriber nhan duoc HealthChangedEvent | yes |
