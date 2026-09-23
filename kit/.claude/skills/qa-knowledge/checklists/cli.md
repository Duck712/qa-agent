# Checklist — Công cụ dòng lệnh

> **Mục checklist là câu hỏi để thử, không phải kỳ vọng.** Kỳ vọng lấy từ tài liệu; tài liệu không nói → điểm hỏi.
> Không chép từ như "tử tế / rõ ràng / OK" vào Kỳ vọng. Trích nguồn trong TC: `Nguồn: <checklist> <số mục>`, vd `form-input 2.3`.

- [ ] 1.1 `--help`, `--version`, không tham số → hành vi theo tài liệu
- [ ] 1.2 Exit code 0 khi thành công, ≠ 0 khi lỗi; lỗi ra stderr, dữ liệu ra stdout
- [ ] 1.3 Cờ lạ, thiếu giá trị cờ, cờ lặp, thứ tự cờ khác
- [ ] 1.4 Đường dẫn có dấu cách, unicode, bắt đầu bằng `-`, tương đối/tuyệt đối, symlink
- [ ] 1.5 File không tồn tại / không có quyền / rỗng / rất lớn / encoding lạ
- [ ] 1.6 Pipe và stdin; output khi không phải TTY (không mã màu); `NO_COLOR`
- [ ] 1.7 Thứ tự ưu tiên cờ > biến môi trường > file config; config hỏng
- [ ] 1.8 Chạy 2 lần (idempotent); file đích đã có; `--dry-run` không ghi gì
- [ ] 1.9 Ctrl-C giữa chừng: không để file dở/khoá treo; chạy lại được
- [ ] 1.10 Cài mới / nâng cấp / gỡ; chạy trên các OS/shell trong phạm vi

## 2. Bổ sung
- [ ] 2.1 Có prompt tương tác mà stdin không phải TTY → không treo (báo lỗi hoặc dùng mặc định theo tài liệu)
- [ ] 2.2 Đầu ra bị ngắt sớm (`| head`) → không in traceback BrokenPipe/SIGPIPE
- [ ] 2.3 Chạy với `LANG=C` / locale khác → không vỡ ký tự, không crash
