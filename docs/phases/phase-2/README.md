# Phase 2 — Trustworthy Feedback Labeling
## AI Facebook Social Listening & Engagement v3

**Status:** Planned
**Depends on:** Phase 1 — Safe Core Loop
**Updated:** 2026-03-29

---

## Goal

Phase 2 tập trung vào một vấn đề chất lượng dữ liệu:

> Làm sao để insight phản ánh tiếng nói của end user, thay vì bị lẫn quá nhiều seller, affiliate, admin, hoặc brand-owned content?

Phase này thêm một lớp **AI labeling cho từng post/comment** và đưa filter tương ứng lên UI để user chủ động chọn góc nhìn phân tích:

- `End-user only`
- `Include seller`
- `Include brand`

Đồng thời thay thế cách exclude thô kiểu `spam_or_seller_noise` bằng cơ chế:

- label rõ ràng
- filter theo policy
- hiển thị `excluded by label` minh bạch trong UI

---

## Expected Outcomes

- Mỗi `POST` và `COMMENT` có label riêng về vai trò tác giả và mức độ liên quan tới feedback người dùng cuối.
- Theme analysis mặc định ưu tiên tiếng nói end user, nhưng vẫn có thể mở rộng để xem seller/brand khi cần.
- User hiểu rõ record nào bị loại khỏi theme analysis và vì sao.
- Dữ liệu thô vẫn được giữ lại để audit hoặc dùng cho use case khác.
- Labeling có lifecycle riêng để hỗ trợ retry, backfill, và taxonomy evolution.

---

## Documents

- [User Stories](./user-stories.md)
- [Architecture](./architecture.md)

---

## Non-goals

- Không làm moderation hoàn hảo 100%.
- Không cố suy luận danh tính thật của tác giả.
- Không auto-delete dữ liệu đã crawl.
- Không thêm workflow manual labeling lớn trong Phase 2.
