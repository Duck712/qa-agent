---
name: qa-targets
description: >
  Cách kiểm thật từng loại target — web, mobile (iOS/Android), API/service, desktop (Electron/native),
  CLI, job/batch/pipeline dữ liệu, tính năng AI/LLM, thư viện/SDK — gồm công cụ điều khiển, công thức theo
  loại test, bằng chứng tối thiểu, và luật an toàn môi trường chung. Nạp skill này khi chọn loại test cho
  một target (lập kế hoạch), khi viết TC cần biết bước nào thực hiện được, và khi chạy test (mở file
  `<loại>.md` tương ứng). Loại chưa có → `khac.md` hướng dẫn tự lập công thức.
---

# qa-targets — kiểm thật từng loại target

## 1. Chọn file

| Loại | Là gì | Công cụ chính | File |
|---|---|---|---|
| `web` | Ứng dụng chạy trên trình duyệt | Playwright MCP (`browser_*`) | [web.md](web.md) |
| `mobile` | App iOS/Android native, RN, Flutter | mobile-mcp trên simulator/emulator | [mobile.md](mobile.md) |
| `api` | REST/GraphQL/gRPC/webhook, service không giao diện | `curl`, `grpcurl`, script Python | [api.md](api.md) |
| `desktop` | Electron, app native macOS/Windows/Linux | Playwright `_electron`, AppleScript/accessibility | [desktop.md](desktop.md) |
| `cli` | Công cụ dòng lệnh, script, installer | Bash trong `qa/sandbox/` | [cli.md](cli.md) |
| `batch` | Job định kỳ, ETL, pipeline dữ liệu, queue worker, báo cáo sinh file | chạy/kích job + so dữ liệu vào/ra | [batch.md](batch.md) |
| `ai` | Chatbot, tóm tắt, phân loại, gợi ý, agent dùng LLM | bộ prompt cố định, chạy lặp, chấm theo tiêu chí | [ai.md](ai.md) |
| `library` | Gói npm/pip/maven, SDK, plugin | chương trình dùng thử trong `qa/sandbox/` | [library.md](library.md) |
| khác | Firmware, game, hệ thống IoT, extension trình duyệt... | tự lập công thức | [khac.md](khac.md) |

Máy chạy QA là **Windows** (tool PowerShell): khối lệnh trong các file trên viết cho Bash → dùng bản PowerShell ở
[windows.md](windows.md) (bẫy PowerShell 5.1, thu stdout/stderr/exit, `curl.exe`, checksum, UI Automation cho app native).

Một sản phẩm thường có nhiều target (web + api + mobile) — mỗi target một dòng `QA.md §Target`, TC ghi
đúng `Target:`. Hành động ở target A phải hiện ở target B → TC loại `cross-target`, bằng chứng cả hai phía.

## 2. Loại test (góc nhìn) — áp cho mọi target

| Loại test | Hỏi câu gì | Ví dụ web | Ví dụ cli/batch/ai |
|---|---|---|---|
| chức năng | Yêu cầu làm được thật không | đặt lịch thành công | lệnh sinh đúng file · job ra đúng số dòng · bot trả lời đúng ý |
| biên | Mép và trạng thái rỗng/lỗi/nhiều | danh sách rỗng, mạng mất | file 0 byte, 1 dòng, 1 triệu dòng · prompt rỗng, rất dài |
| phá-đầu-vào | Đầu vào xấu có bị xử lý đúng | injection, 10k ký tự, double-submit | cờ sai, unicode trong path · dòng hỏng giữa file · prompt injection |
| phân-quyền | Vai/tenant không được phép có bị chặn ở server | gọi thẳng API vai thấp | chạy lệnh không đủ quyền file · job đọc dữ liệu tenant khác · bot lộ dữ liệu người khác |
| workflow | Chuỗi nhiều bước/vai/trạng thái | tạo → duyệt → đóng | pipeline nhiều chặng · hội thoại nhiều lượt |
| api | Hành vi server bỏ qua giao diện | validate phía server | — |
| tích-hợp | Dịch vụ ngoài và phụ thuộc | email/thanh toán sandbox | nguồn dữ liệu chết giữa job · model provider lỗi/timeout |
| tương-thích | Bản cũ, dữ liệu cũ, môi trường khác | trình duyệt, API version cũ | OS/shell khác · file định dạng cũ · version thư viện cũ |
| hình-thức | Giao diện đúng design, a11y | computed style so token | output dễ đọc, `--help` rõ, màu terminal tắt được |
| hiệu-năng | Đủ nhanh ở mức dùng thường | thời gian tải (median/max) | thời gian chạy job theo kích thước dữ liệu · độ trễ/chi phí mỗi lượt gọi model |
| bảo-mật | Lớp bảo vệ cơ bản (chỉ khi được phép) | header, phiên, IDOR | secret trong log/output · path traversal · dữ liệu nhạy cảm trong prompt/response |
| cross-target | Hành động ở A hiện đúng ở B | admin đổi giá → khách thấy giá mới | job ghi → báo cáo/API đọc thấy · bot gọi tool → hệ đơn hàng đổi |
| khám-phá | Thăm dò theo charter, tìm rủi ro chưa có TC | tour tính năng | tour dữ liệu xấu với lệnh/job/prompt |
| smoke | Luồng lõi còn chạy sau deploy | đăng nhập + luồng chính | lệnh chính · job mẫu nhỏ · câu hỏi mẫu |
| khôi-phục | Hỏng giữa chừng rồi ra sao | đóng tab giữa form | Ctrl-C giữa lệnh · job chết giữa chừng chạy lại · retry trùng |

## 3. An toàn — áp cho mọi target

1. **Chỉ đứng trong vùng test**: tài khoản/tenant/thư mục/bucket test khai ở `QA.md`. Bản ghi/file tạo ra
   mang prefix `QA-<run-id>-`. Không ghi/sửa/xoá thứ không mang prefix — trên staging dùng chung, đó là
   dữ liệu của người khác. Thấy dữ liệu người thật → chụp bằng chứng (che dữ liệu cá nhân), dừng, báo S1.
2. **Dữ liệu tạo/dọn qua đường chính thức** (UI/API/lệnh của sản phẩm). Không chạm thẳng DB production.
   Staging chỉ khi SCOPE ghi cho phép.
3. **Hướng ra ngoài**: email/SMS/push chỉ tới địa chỉ test; thanh toán chỉ sandbox; webhook trỏ endpoint
   của QA. Không có đường test → TC `BLOCKED`, không "thử đại" vào địa chỉ thật.
4. **Nhịp độ** (nguồn duy nhất — file khác trỏ về đây): trần an toàn mỗi phép đo/lặp là 20 lời gọi, giãn cách ≥ 1s
   (vượt trần → hỏi). Số lần cụ thể, số kích thước dữ liệu, số request đồng thời: QA đề xuất kèm lý do và hỏi; đã chốt
   thì ghi SCOPE §7 hoặc DECISIONS. Báo median + max kèm n; phân vị (p95…) chỉ khi người dùng chốt cỡ mẫu đủ cho nó.
   Thấy 429 thì dừng. Load/stress **chỉ** khi SCOPE §7 khai
   môi trường riêng — không bao giờ trên production hay máy dùng chung.
5. **Bảo mật**: chỉ chứng minh lỗ, không khai thác phá; active scan chỉ khi người dùng cho phép rõ. **Ranh giới**: chuỗi
   phá-đầu-vào tiêu biểu (một chuỗi mỗi ô, chỉ quan sát hiển thị/mã lỗi) và ca AI đại diện (checklist ai-llm 1.5–1.7, 1.9)
   là test thường; payload có mục đích khai thác (UNION, time-based, SSRF, nhiều biến thể, jailbreak nhiều lượt có chủ
   đích, rò secret/hạ tầng) hoặc **bất kỳ** chuỗi injection nào trên `Môi trường: production` → bảo mật, cần SCOPE §7.
6. **Không nhầm môi trường**: trước khi chạy, so URL/host/bundle/lệnh thật với `QA.md §Môi trường`. Lệch → dừng, báo.
7. **Hàng rào kỹ thuật có giới hạn**: quyền `ask` cho psql/mysql… và hook không phủ lệnh chạy qua `ssh <máy> "…"` hay
   `docker … exec` — luật ở đây vẫn áp nguyên vẹn cho các lệnh đó; chạm DB qua đường nào cũng cần SCOPE §7 cho phép.
8. **Lệnh phá hoại** (`rm -rf`, `DROP`, `kubectl delete`, `terraform destroy`, xoá bucket) chỉ trong
   `qa/sandbox/` hoặc tài nguyên có prefix QA — ngoài đó phải hỏi.
9. **Thiếu công cụ** (grpcurl, websocat, xdotool, testssl.sh, simulator…) → TC dùng nó `BLOCKED`, ghi lệnh cài đề
   xuất và báo người dùng; **không tự cài** (brew/pip/npm toàn máy), không tự đổi cấu hình máy/MCP.
10. **Máy dùng chung**: giới hạn worker/song song theo `QA.md §Môi trường` (chưa có → hỏi), đóng trình duyệt/simulator/
   tiến trình nền khi xong; việc cần container hay chạy lâu → theo quy ước máy/đội của người dùng, không tự dựng hạ tầng.
11. **Khảo sát giao diện chưa rõ** (web / desktop / mobile; bài học từ dự án): không dùng script bấm hàng loạt mục menu /
   nút — mục lá có thể mở màn xử lý hoặc tự chạy việc gì đó. Lấy cây menu từ dữ liệu (API, model phía client), mở từng
   màn và chỉ đọc. Lỡ mở / bấm hàng loạt → dừng ngay, kiểm dấu vết (ô "lần chạy trước", log, lịch sử) xác nhận chưa có
   xử lý nào chạy, báo người dùng và ghi LESSONS.
