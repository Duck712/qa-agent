# Target `cli` — công cụ dòng lệnh, script, installer

## Chạy bằng gì
Bash, trong thư mục riêng mỗi TC: `qa/sandbox/<run-id>/<TC-ID>/` (không commit). Dùng bản được giao
(binary/gói/version ở `QA.md §Target`), không chạy thẳng từ code nguồn trừ khi đó chính là cách phát hành.

Ghi mỗi lệnh thành bằng chứng:
```bash
D=qa/evidence/$RUN/$TC; S=qa/sandbox/$RUN/$TC; mkdir -p $D $S
( cd $S && echo '$ tool convert in.csv --out out.json' && tool convert in.csv --out out.json ) \
  > $D/01-stdout.txt 2> $D/01-stderr.txt; echo "exit=$?" > $D/01-exit.txt
cp $S/out.json $D/01-out.json 2>/dev/null
```

## Công thức
- **Chức năng**: mỗi lệnh con/cờ trong tài liệu chạy đúng · output đúng định dạng (JSON hợp lệ: `python3 -m json.tool`).
- **Exit code**: thành công = 0, lỗi ≠ 0 và khác nhau theo loại lỗi nếu tài liệu nói vậy; lỗi ra **stderr**, dữ liệu ra **stdout**.
- **Đầu vào xấu**: cờ lạ, thiếu tham số bắt buộc, file không tồn tại/không có quyền đọc, file rỗng, file rất lớn, encoding lạ (UTF-16, BOM), đường dẫn có dấu cách/unicode/`-` ở đầu.
- **`--help` / `--version`**: có, đúng, khớp tài liệu.
- **Pipe / stdin / TTY**: `cat in | tool -` · output khi không phải TTY (không mã màu, không spinner) · `NO_COLOR`.
- **Biến môi trường & config**: thứ tự ưu tiên cờ > env > file config; config hỏng thì báo gì.
- **Ghi đè / idempotent**: chạy 2 lần liên tiếp; file đích đã tồn tại; `--dry-run` thật sự không ghi.
- **Ngắt giữa chừng** (Ctrl-C thật = SIGINT; macOS không có `timeout`):
  `python3 -c "import subprocess,signal,time,sys; p=subprocess.Popen(sys.argv[1:]); time.sleep(2); p.send_signal(signal.SIGINT); print('exit', p.wait())" tool convert big.csv --out out.json`
  → không để file dở/khoá treo, chạy lại được.
- **Cài đặt**: cài sạch, nâng cấp từ bản cũ, gỡ; chạy trên shell/OS khác nếu trong phạm vi.
- **Hiệu năng**: `/usr/bin/time -l` (macOS) / `-v` (Linux) với 3 kích thước đầu vào.

## Bằng chứng tối thiểu
Lệnh nguyên văn + stdout + stderr + exit code + file output (hoặc checksum nếu lớn) + version tool (`tool --version`).
