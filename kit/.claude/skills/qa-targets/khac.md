# Target khác — tự lập công thức

Firmware/IoT, game, extension trình duyệt, plugin IDE, hệ thống phần cứng, bot chat trên nền tảng thứ ba,
hạ tầng (IaC, Helm chart)... Chưa có file riêng thì lập công thức trước khi viết TC, trả lời 5 câu:

1. **Điều khiển bằng gì?** Công cụ nào thao tác được như người dùng thật (UI automation, lệnh, API, thiết bị
   giả lập, emulator phần cứng)? Không có công cụ → phần đó là TC `Thực hiện: người` (người dùng duyệt), QA viết TC +
   checklist và ghi kết quả người làm báo lại theo skill `qa` §7 (bằng chứng họ gửi + `nguoi-thuc-hien.md`).
2. **Quan sát bằng gì?** Màn hình, log, trạng thái thiết bị, dữ liệu đích — thứ nào chứng minh được kết quả?
3. **Bằng chứng tối thiểu** cho PASS là gì? (ghi vào SCOPE §4 để cả lượt dùng chung)
4. **Vùng an toàn** là gì? (thiết bị test, tài khoản sandbox của nền tảng, namespace/cluster test)
5. **Góc nhìn nào áp dụng?** Duyệt bảng loại test ở `SKILL.md §2`, bỏ loại không hợp có lý do.

Trình 5 câu trả lời cho người dùng **duyệt trước khi test** — đồng ý thì ghi vào `SCOPE.md §4` (cột "Bằng chứng tối
thiểu / vùng an toàn") và một dòng `DECISIONS.md` trích lời duyệt. Công thức dùng tốt qua nhiều dự án → đề xuất người
dùng thêm thành file `<loại>.md` mới trong skill này.

Gợi ý nhanh:
| Loại | Điều khiển / quan sát |
|---|---|
| Extension trình duyệt | Playwright `launchPersistentContext` với `--load-extension` |
| Bot Slack/Discord/Telegram | Workspace/bot test, gọi API nền tảng bằng tài khoản test, đọc tin nhắn trả về |
| IaC / Helm / Terraform | `terraform plan` / `helm template` + policy check; apply chỉ trên môi trường sandbox có prefix |
| Firmware / IoT | Emulator (QEMU, Renode) hoặc thiết bị test; log serial; không có → thủ công do người dùng |
| Game | Build test + bot input nếu engine hỗ trợ; phần cảm nhận → thủ công |
