# CP2 — Browser Session Setup

**Code:** cp2-browser-session
**Order:** 2
**Depends On:** cp1-schema-lock
**Estimated Effort:** 1.5 ngay

## Muc tieu

Implement BrowserAgent voi Camoufox persistent profile. User co the dang nhap Facebook 1 lan qua browser visible, session duoc luu va reuse o lan chay tiep theo. API `/api/browser/status` va `/api/browser/setup` hoat dong.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| backend/app/infra/browser_agent.py | created | Camoufox wrapper voi persistent profile, wait_for_login(), is_logged_in(), assert_session_valid() |
| backend/app/api/browser.py | created | GET /api/browser/status, POST /api/browser/setup, GET /api/browser/setup/stream |
| backend/app/schemas/browser.py | created | Pydantic schemas cho browser API |
| backend/app/main.py | modified | Register browser router |
| frontend/src/pages/SetupPage.tsx | created | Setup screen hien thi trang thai session va huong dan login |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | GET /api/browser/status tra ve session_status=NOT_SETUP khi chua login | yes |
| CHECK-02 | POST /api/browser/setup mo Camoufox browser visible (headless=False) | yes |
| CHECK-03 | Sau khi user login Facebook trong browser, GET /api/browser/status tra ve session_status=VALID va account_id_hash khac null | yes |
| CHECK-04 | Restart backend → GET /api/browser/status van tra ve VALID (session persist qua browser profile) | yes |
| CHECK-05 | browser_profile directory duoc tao trong ~/.social-listening/ | yes |
| CHECK-06 | account_id_hash la HMAC-SHA256, khong chua plaintext FB user ID | no |
| CHECK-07 | SetupPage hien thi huong dan va cap nhat trang thai khi login xong | no |
