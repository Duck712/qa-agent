# Dữ liệu test, test tự động, TC do người chạy tay — chi tiết của skill `qa` §7

> Khi nào đọc + luật luôn phải nhớ: skill `qa` §7.

**Dữ liệu test (việc 6)** — trước khi tạo gì, hỏi (nếu `QA.md` chưa ghi): tạo/dọn bằng đường nào được phép (UI, API,
lệnh của sản phẩm; chạm DB chỉ khi SCOPE §7 cho phép), tài khoản/tenant nào dùng được, dữ liệu nào không được đụng.
Rồi:
- Script seed/dọn đặt ở `qa/scripts/seed.<ext>` và `qa/scripts/cleanup.<ext>`; mọi bản ghi mang prefix `QA-<run-id>-`;
  `cleanup` chỉ xoá bản ghi có prefix, in danh sách đã xoá (đó là bằng chứng đã dọn). Bí mật đọc từ `qa/.env`.
- Chạy seed trước run, ghi vào `## Nhật ký` của RUNLOG; hết run (hoặc hết nhóm phá-đầu-vào/phân-quyền) **hỏi người
  dùng** có dọn không rồi chạy cleanup — trên môi trường dùng chung, mặc định đề xuất dọn.
- Thứ không dọn được qua đường chính thức → ghi `## Nhật ký` "rác còn lại", báo người dùng.

**Test tự động (việc 12)** — hỏi trước khi viết: framework (theo cái đội đang dùng nếu có — xem code/test sẵn có),
nơi đặt (`qa/automation/` mặc định; repo sản phẩm chỉ khi người dùng nhờ rõ và gỡ đường dẫn khỏi `Chỉ đọc:`), chạy ở
đâu (máy local / CI / môi trường riêng), dữ liệu test lấy từ đâu. Rồi:
- Một script ↔ một hoặc vài TC, tên file chứa TC-ID; không đổi kỳ vọng của TC khi viết script.
- Phụ thuộc chỉ cài trong `qa/automation/` và **chỉ sau khi người dùng đồng ý** (DECISIONS); không cài toàn máy.
- Chạy thật; output (report của framework, stdout, ảnh) ghi vào `qa/evidence/<run-id>/<TC-ID>/` — đó là bằng chứng,
  kết quả ghi RUNLOG như chạy tay. Script lỗi do chính script (không phải sản phẩm) → sửa script, không ghi FAIL.

**TC do người chạy tay** (`Thực hiện: người`) — khi agent không điều khiển được target/bước (thiết bị thật, phần cứng, máy
in, hộp thoại hệ thống, Ctrl-C thật, cảm nhận game…) hoặc đội giao TC cho tester người. Đặt `Thực hiện: người` là quyết
định của người dùng (đề xuất kèm lý do, họ duyệt). Rồi:
- `new-run` ghi danh sách TC này vào RUNLOG. Giao cho người ở `QA.md §Người chạy TC thủ công`: TC-ID, bước, kỳ vọng,
  `Bằng chứng cần`, thư mục bằng chứng `qa/evidence/<run-id>/<TC-ID>/`, môi trường/bản phải dùng.
- Người làm gửi kết quả + bằng chứng (ảnh, video, file, ghi chú) → agent chép vào đúng thư mục TC, thêm
  `nguoi-thuc-hien.md`: ai làm (vai/nhóm — không cần họ tên nếu đội không muốn), lúc nào, môi trường/bản, bằng chứng
  nhận qua đâu, và **nguyên văn** kết quả họ báo. `qa_check.py run` báo lỗi khi PASS/FAIL thiếu file này.
- Agent **không** tự chấm thay: ghi đúng kết quả người làm báo; bằng chứng không chứng minh được kỳ vọng (ảnh thiếu bước,
  "đã test OK" không kèm gì) → hỏi lại người làm, chưa đủ thì `BLOCKED`. Lệch kỳ vọng → `FAIL` + `/qa-bug` như thường.
- Không có ai chạy tay được → TC `BLOCKED` (lý do: chờ người thực hiện), không đổi thành agent chạy bằng cách đoán.
