# Phase 5 — Resilient AI Routing & Release Notes
## AI Facebook Social Listening & Engagement v3

**Status:** Scope locked from BA brief and ready for implementation
**Depends on:** Phase 4 — Shared Shell UI Refactor
**Updated:** 2026-03-29

---

## Goal

Phase 5 tap trung vao 2 van de user-facing va 1 van de reliability:

- dua model marketplace OpenAI-compatible thanh duong goi mac dinh cho cac AI request
- chi fallback sang Claude khi request marketplace bi timeout
- dua release note cua tung phase vao ngay trong product shell de end user nhin thay thay doi moi ma khong can mo docs
- dong bo ten hien thi cua app voi phase hien hanh theo format `Social Listening v3.{phase}`

---

## Expected Outcomes

- AI runtime uu tien `https://llm.chiasegpu.vn/v1` cho chat completion
- Claude van duoc giu lam fallback provider khi timeout, khong bi loai bo
- Product shell co link release note dan toi mot page doc duoc, dep, than thien
- Phase 5 co release note rieng duoc attach tu luc user stories da chot
- Header va browser title hien thi `Social Listening v3.5`

---

## Documents

- [BA Problem Brief](./ba-problem-brief.md)
- [User Stories](./user-stories.md)
- [Release Note Payload](./release-note.json)

BA brief la source of truth cho problem framing. User stories la source of truth cho implementation scope.
