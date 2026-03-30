# BA Problem Brief — Phase 5

## Metadata

- Initiative: Phase 5 — Resilient AI Routing & Release Notes
- Owner: Social Listening v3 product/runtime team
- Related research: production behavior of current Claude-only AI flow, Phase 4 shared shell output
- Primary layer: App runtime + Shared Product Shell

## Problem

- Problem statement:
  Social Listening v3 hien dang goi Claude la duong AI mac dinh. User muon chuyen sang endpoint marketplace OpenAI-compatible de lam default runtime path, nhung van phai giu Claude lam fallback khi timeout. Dong thoi, app chua co release note page cho end user va ten shell chua phan anh phase hien hanh.
- Who is affected:
  researcher, marketer, sales/BD user, va team van hanh app
- Why this matters:
  runtime AI can on dinh hon va linh hoat hon theo nha cung cap; end user nhin thay thay doi theo phase ro rang hon; shell can nhat quan voi cadence phat hanh
- Current cost of problem:
  AI path bi khoa chat vao Claude; release changes bi an trong docs/noi bo; header khong cho user biet app dang o phase nao

## Desired Outcome

- Target user/business outcome:
  moi AI request mac dinh chay qua marketplace endpoint; neu timeout moi retry sang Claude; release note cua phase hien hanh co link cong khai ngay trong app; shell title hien thi `Social Listening v3.5`
- Success signals:
  request AI thanh cong qua provider mac dinh khi key hop le; timeout thi fallback khong lam vo pipeline; header hien thi dung phase; release note page load duoc va doc de hieu cho end user

## Stakeholders

| Stakeholder | Need | Power | Risk if ignored |
|---|---|---|---|
| End user | biet phase moi thay doi gi, co anh huong nao toi workflow cua ho | High | release xong nhung user khong biet gia tri moi |
| Product owner | co artifact phase ro rang va thong diep phat hanh chuan | High | scope phase bi tro thanh wish list va khong co handoff ro |
| Backend/runtime engineer | 1 duong AI routing trung tam, de monitor va fallback | High | moi service tu xu ly provider rieng, tang bug |
| Frontend engineer | metadata phase va release note co source of truth ro | Medium | UI hard-code, doi phase phai sua nhieu noi |
| Ops/support | hieu luc nao fallback sang Claude, luc nao khong | Medium | debugging provider failure mo ho |

## Current State

- Current flow:
  `AIClient` goi Claude truc tiep neu co `ANTHROPIC_API_KEY`, neu khong thi tra mock response
- Current systems:
  backend co 1 AI abstraction trung tam; frontend shell da duoc Mantine-hoa o Phase 4; `.phase.json` ton tai nhung chua duoc UI dung
- Current constraints:
  app khong co router framework; release note chua co data contract; can tranh sua moi service AI mot cach phan tan

## Future State

- Target flow:
  service -> `AIClient` -> marketplace endpoint (`/v1/chat/completions`) -> neu timeout thi retry sang Claude -> parse/repair JSON -> service dung lai nhu cu
- Target operating model:
  moi phase co `user-stories.md` va `release-note.json`; shell doc runtime metadata de hien thi ten phase va link release note hien hanh

## Requirement Split

### Shared Business Platform

- Khong co requirement moi cho billing/workspace/auth. Phase nay khong doi platform ownership.

### Shared Product Shell

- Shell phai hien thi ten app theo phase hien hanh, dang `Social Listening v3.{n}`
- Shell phai co link release note de mo mot page doc than thien cho end user
- Release note page phai lay du lieu tu artifact theo phase, khong hard-code trong component

### App Runtime

- `AIClient` phai uu tien endpoint marketplace OpenAI-compatible lam default provider
- Claude chi duoc retry khi request default provider bi timeout
- Fallback logic phai tap trung o 1 abstraction, khong trai ra tung service
- Runtime metadata phai expose current phase, display name, va release note availability cho frontend

## Constraints

- Technical:
  khong nen dua router framework lon vao chi de phuc vu 1 page release note; can giu AI integration tap trung va backward-compatible voi mock mode
- Legal/policy:
  API key phai di qua env/config, khong hard-code secret
- Team/resource:
  phase nay nen tan dung docs + shell foundation da co, tranh tao CMS rieng
- Dependency:
  can `.phase.json` va release note artifact ton tai dung phase; Claude API van can giu de fallback

## Non-goals

- Khong doi nghiep vu plan/crawl/approve/theme analysis
- Khong lam multi-page router day du cho toan bo app
- Khong them he thong CMS/release management ben ngoai repo
- Khong fallback sang Claude cho moi loai loi khac timeout

## Open Questions

- Timeout threshold chot cho marketplace call la bao nhieu giay trong production
- Release note co can track lich su nhieu phase tren UI hay chi phase hien hanh
- Co can telemetry rieng de phan biet provider mac dinh vs fallback trong future phase khong

## Recommendation

- Next artifact:
  khoa scope phase 5 bang user stories US-50 -> US-53, tao release note payload cho phase 5, va implement runtime metadata + shell integration tren cung 1 source of truth
