# ANALYSIS — {{PROJECT_NAME}}

> `/qa-analyze` — kỹ thuật: `qa-knowledge/analysis-review.md`. Dịch tài liệu (và code) thành thứ test được. Mỗi yêu cầu một mã `REQ-<TÍNH-NĂNG>-<số>` —
> TC sẽ trỏ về mã này. Chỉ ghi điều tài liệu nói; điều tài liệu KHÔNG nói → mục 5.

## 1. Tổng quan sản phẩm
<!-- 3–5 dòng: sản phẩm làm gì, ai dùng, target nào (web/mobile/api/desktop/cli/batch/ai/library) -->

## 2. Vai người dùng & ma trận quyền
| Vai | Mô tả |
|---|---|
| | |

<!-- Ma trận quyền (khuôn gen_matrix_tc.py đọc): vai là cột, mỗi hành động một dòng; ✓ = được, ✗ = bị cấm, ô chưa rõ
     để `?` và hỏi. Hành động trên bản ghi của người khác / tenant khác là dòng riêng. -->
| Hành động | <vai 1> | <vai 2> | chưa đăng nhập |
|---|---|---|---|
| | | | |

## 3. Yêu cầu (tính năng → yêu cầu test được)
<!-- REQ rút từ code, hoặc phụ thuộc điểm chưa rõ → thêm `(chờ trả lời #n)` vào cột Mô tả; gỡ khi người dùng trả lời. -->
| REQ | Tính năng | Mô tả yêu cầu (hành vi quan sát được) | Target | Nguồn (file/mục) |
|---|---|---|---|---|
| | | | | |

## 4. Mô hình: use case · trạng thái · CRUD
<!-- Use case: luồng chính + thay thế (2a…) + ngoại lệ từng bước. Trạng thái: bảng trạng thái × sự kiện (ô ? = hỏi).
     CRUD: thực thể × C/R/U/D × vai. Chỉ vẽ phần có trong phạm vi. -->

## 5. Điểm mơ hồ / thiếu / mâu thuẫn
<!-- Mỗi dòng: điểm chưa rõ / lệch tài liệu↔code + đề xuất của QA + rủi ro nếu hiểu sai. Hỏi người dùng, không tự điền. -->
| # | Điểm chưa rõ | Đề xuất | Rủi ro nếu sai | Trả lời |
|---|---|---|---|---|
| | | | | |

## 6. Rủi ro (analysis-review §7) — mức ở đây là ĐỀ XUẤT, người dùng xác nhận ở SCOPE §2
| REQ / tính năng | Xác suất lỗi (1–3) | Thiệt hại (1–3) | Rủi ro | Mức đề xuất | Lý do |
|---|---|---|---|---|---|
| | | | | | |

## 7. Yêu cầu ngầm / phi chức năng (ISO 25010 — analysis-review §4)
| Đặc tính | Tài liệu nói gì | Đề xuất / câu hỏi (#) |
|---|---|---|
| Chức năng (đủ, đúng, phù hợp) | | |
| Hiệu năng | | |
| Tương thích (cùng tồn tại, tương tác hệ khác) | | |
| Khả dụng / a11y | | |
| Tin cậy / khôi phục | | |
| Bảo mật / quyền riêng tư | | |
| Bảo trì / vận hành (log, cấu hình) | | |
| Linh hoạt (cài đặt, nâng cấp, nền tảng, bản địa hoá) | | |
| An toàn (hệ có thể gây hại người/tài sản) | | |

## 8. Thay đổi & ảnh hưởng (analysis-review §8)
<!-- Bản này đổi gì so với bản trước (changelog, git diff) → tính năng bị chạm trực tiếp / dùng chung thành phần -->
