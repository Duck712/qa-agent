# Target `api` — REST / GraphQL / gRPC / webhook

## Chạy bằng gì
`curl` (REST, GraphQL), `grpcurl` (gRPC), `websocat` (WebSocket), script Python chuẩn (`urllib`) cho kịch bản
nhiều bước. Công cụ chưa cài → BLOCKED + đề xuất lệnh cài, không tự cài. Token/mật khẩu nạp từ `qa/.env` bằng `set -a; . qa/.env; set +a` (tool Read bị chặn đọc file này) — **không in ra màn hình, che trong bằng chứng**.

> Mỗi khối lệnh dưới là **một** lệnh Bash: biến không giữ giữa các lần gọi. Tool Read bị chặn đọc `qa/.env` —
> nạp bí mật bằng `set -a; . qa/.env; set +a` trong cùng lệnh, không in ra.

Lưu mỗi lời gọi thành bằng chứng ngay khi chạy (Windows/PowerShell: [windows.md](windows.md) §3 — `curl.exe`, body qua file):
```bash
RUN=<run-id>; TC=<TC-ID>; set -a; . qa/.env; set +a   # BASE, TOKEN_B… trong qa/.env
D=qa/evidence/$RUN/$TC; mkdir -p "$D"
BODY='{"name":"QA-'$RUN'-o1"}'                       # body thật — dùng lại cho cả request và file bằng chứng
curl -sS -X POST "$BASE/api/orders" -H "Authorization: Bearer $TOKEN_B" -H 'Content-Type: application/json' \
  -d "$BODY" -o $D/01-response.json -w 'HTTP %{http_code} · %{time_total}s\n' \
  -D $D/01-headers.txt | tee $D/01-status.txt
printf 'POST %s/api/orders (token vai B)\n%s\n' "$BASE" "$BODY" > $D/01-request.txt
```

Tìm bề mặt API: OpenAPI/Postman nếu có; không có hoặc nghi thiếu → đọc route/handler trong code (liệt kê mọi
endpoint, method, middleware quyền) — endpoint có trong code mà không có trong tài liệu là điểm hỏi người dùng
(và là chỗ hay quên phân quyền).

## Công thức
- **Contract**: so response với tài liệu/OpenAPI — trường thiếu/thừa, kiểu, định dạng ngày, mã lỗi, envelope lỗi thống nhất.
- **Validate ở server** (bỏ qua UI): thiếu trường bắt buộc, sai kiểu, vượt độ dài, giá trị âm, enum lạ, JSON hỏng → bị từ chối có thông điệp, không 500 (mã 4xx cụ thể theo API doc; không có → hỏi).
- **Phân trang / lọc / sắp xếp**: trang rỗng, trang cuối đúng mép (`limit=10` với 10 bản ghi), `page=-1`, `limit=100000`, ký tự `%` `_` `'` trong filter.
- **Phân quyền**: mỗi ô ✗ ma trận vai × hành động một lời gọi thẳng → bị chặn (mã theo API doc); đổi id sang bản ghi/tenant khác (IDOR); endpoint phụ (export, download, autocomplete) hay bị quên.
- **Idempotency / đồng thời**: gửi cùng request 2 lần song song (`& wait`), retry với cùng `Idempotency-Key`.
- **Method / header**: method không hỗ trợ → bị từ chối (mã theo API doc; không có → hỏi); thiếu `Content-Type`; CORS từ origin lạ; cache header trên dữ liệu riêng tư.
- **Webhook**: endpoint nhận của QA (server tạm trong `qa/sandbox/`), kiểm chữ ký, retry, thứ tự, trùng lặp. Cổng/sandbox
  bên ngoài cần gọi tới được URL công khai → **hỏi** người dùng (tunnel, hoặc dùng log webhook của cổng/staging); không
  tự dựng tunnel hay mở cổng máy dùng chung ra ngoài.
- **Tương thích**: gọi version cũ (`/v1`) và client cũ; so với bề mặt API ghi lần trước (lưu `qa/API-SURFACE.md` nếu đội cần theo dõi).
- **Rate limit**: số lời gọi vừa đủ vượt ngưỡng tài liệu nêu (không nêu → hỏi; vượt trần an toàn `qa-targets` §3 mục 4 → hỏi), thấy 429 là xác nhận có chặn, dừng.
- **Hiệu năng**: `-w '%{time_total}'` lặp theo nhịp đã chốt (`qa-targets` §3 mục 4), báo median + max kèm n; ngưỡng do tài liệu/người dùng cho.

## Bằng chứng tối thiểu
Request (method, URL, header đã che, body) + response nguyên văn (mã + header + body) + thời điểm.
