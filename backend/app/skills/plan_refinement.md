PLAN_REFINEMENT

Input la current plan va natural language instruction.

Rules:
- Tang version moi khi refine.
- Neu instruction giam pham vi, co the bo bot steps hoac giam estimated_count.
- Tra ve diff_summary ngan gon.
- Tra ve duy nhat 1 JSON object hop le, khong markdown, khong prose.
- Chi giu cac action_type nam trong action registry duoc inject ben duoi.
- Neu mot step phu thuoc vao action khong duoc support thi loai bo step do thay vi de dependency mo coi.
- Khi refine, uu tien giu flow post-first cho moi keyword cluster:
  SEARCH_POSTS -> CRAWL_COMMENTS -> JOIN_GROUP(private) -> CHECK_JOIN_STATUS -> SEARCH_IN_GROUP
- SEARCH_POSTS.target phai la 1 search phrase ngan gon, thuc su go duoc vao Facebook search bar.
- SEARCH_IN_GROUP.target phai co dang `keyword:{phrase} in groups from step-N`.
- Khong duoc de target dang `brand: A, B, C` hoac list keyword dai.
- Giu schema giong plan generation:
  {
    "steps": [...],
    "warnings": ["string"],
    "estimated_total_duration_sec": 600,
    "diff_summary": "string"
  }
