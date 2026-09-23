# Target `api` — REST / GraphQL / gRPC / webhook

## Chạy bằng gì
`curl` (REST, GraphQL), `grpcurl` (gRPC), `websocat` (WebSocket), script Python chuẩn (`urllib`) cho kịch bản
nhiều bước. Token/mật khẩu đọc từ `qa/.env` — **không in ra màn hình, che trong bằng chứng**.

Lưu mỗi lời gọi thành bằng chứng ngay khi chạy:
```bash
D=qa/evidence/$RUN/$TC; mkdir -p $D
curl -sS -X POST "$BASE/api/orders" -H "Authorization: Bearer $TOKEN_B" -H 'Content-Type: application/json' \
  -d '{"name":"QA-'$RUN'-o1"}' -o $D/01-response.json -w 'HTTP %{http_code} · %{time_total}s\n' \
  -D $D/01-headers.txt | tee $D/01-status.txt
echo "POST $BASE/api/orders (token vai B) body={...}" > $D/01-request.txt
```

Tìm bề mặt API: OpenAPI/Postman nếu có; không có hoặc nghi thiếu → đọc route/handler trong code (liệt kê mọi
endpoint, method, middleware quyền) — endpoint có trong code mà không có trong tài liệu là điểm hỏi người dùng
(và là chỗ hay quên phân quyền).

## Công thức
- **Contract**: so response với tài liệu/OpenAPI — trường thiếu/thừa, kiểu, định dạng ngày, mã lỗi, envelope lỗi thống nhất.
- **Validate ở server** (bỏ qua UI): thiếu trường bắt buộc, sai kiểu, vượt độ dài, giá trị âm, enum lạ, JSON hỏng → 4xx có thông điệp, không 500.
- **Phân trang / lọc / sắp xếp**: trang rỗng, trang cuối đúng mép (`limit=10` với 10 bản ghi), `page=-1`, `limit=100000`, ký tự `%` `_` `'` trong filter.
- **Phân quyền**: mỗi ô ✗ ma trận vai × hành động một lời gọi thẳng → 401/403/404; đổi id sang bản ghi/tenant khác (IDOR); endpoint phụ (export, download, autocomplete) hay bị quên.
- **Idempotency / đồng thời**: gửi cùng request 2 lần song song (`& wait`), retry với cùng `Idempotency-Key`.
- **Method / header**: method không hỗ trợ → 405; thiếu `Content-Type`; CORS từ origin lạ; cache header trên dữ liệu riêng tư.
- **Webhook**: endpoint nhận của QA (server tạm trong `qa/sandbox/`), kiểm chữ ký, retry, thứ tự, trùng lặp.
- **Tương thích**: gọi version cũ (`/v1`) và client cũ; so với bề mặt API ghi lần trước (lưu `qa/API-SURFACE.md` nếu đội cần theo dõi).
- **Rate limit**: tối đa 20 lời gọi, giãn cách; thấy 429 là xác nhận có chặn, dừng.
- **Hiệu năng**: `-w '%{time_total}'` lặp n ≤ 20, giãn ≥ 1s, báo p50/p95.

## Bằng chứng tối thiểu
Request (method, URL, header đã che, body) + response nguyên văn (mã + header + body) + thời điểm.
