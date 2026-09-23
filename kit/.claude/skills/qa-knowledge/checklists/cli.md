# Checklist — Công cụ dòng lệnh

- [ ] `--help`, `--version`, không tham số → hành vi theo tài liệu
- [ ] Exit code 0 khi thành công, ≠ 0 khi lỗi; lỗi ra stderr, dữ liệu ra stdout
- [ ] Cờ lạ, thiếu giá trị cờ, cờ lặp, thứ tự cờ khác
- [ ] Đường dẫn có dấu cách, unicode, bắt đầu bằng `-`, tương đối/tuyệt đối, symlink
- [ ] File không tồn tại / không có quyền / rỗng / rất lớn / encoding lạ
- [ ] Pipe và stdin; output khi không phải TTY (không mã màu); `NO_COLOR`
- [ ] Thứ tự ưu tiên cờ > biến môi trường > file config; config hỏng
- [ ] Chạy 2 lần (idempotent); file đích đã có; `--dry-run` không ghi gì
- [ ] Ctrl-C giữa chừng: không để file dở/khoá treo; chạy lại được
- [ ] Cài mới / nâng cấp / gỡ; chạy trên các OS/shell trong phạm vi
