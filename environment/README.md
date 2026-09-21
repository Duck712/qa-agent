# environment/ — mọi thứ để CHẠY môi trường test, tách khỏi tài liệu

> Tài liệu môi trường (URL, tài khoản, tenant, mốc dữ liệu) nằm ở `context/ENVIRONMENT.md`.
> **Artifact chạy** nó — seed script, plan dữ liệu, biến env — nằm ở đây. Pha P viết vào.

```
environment/
├── .env.example      ← danh sách TÊN biến (file duy nhất được commit ở dạng "có nội dung env")
└── local/            ← seed script · plan-B1.yaml · .env thật (KHÔNG commit)
```

## Luật

1. **`.env.example` chỉ có TÊN biến + mô tả, không bao giờ có giá trị thật.** `make doctor`
   đọc nó để biết biến nào bắt buộc. Giá trị thật ở `environment/local/.env` —
   `.gitignore` chặn `.env` mọi cấp.
2. **Seed/reset đi QUA API của sản phẩm** bằng tài khoản test — script ở `local/`,
   idempotent, mọi bản ghi tạo ra mang prefix `SPEC-r<N>-`. **CẤM chạm thẳng DB
   production** (luật #6, `shared/SAFETY.md`); staging chỉ khi `TEST-STRATEGY §8` cho phép. QC cấp seed endpoint qua manifest thì được
   dùng — giới hạn tenant test, ghi nguồn vào `ENVIRONMENT.md §5`.
3. **`plan-B1.yaml` là dữ liệu mẫu ĐỌC ĐƯỢC** — khai theo persona (ai có bản ghi gì),
   để QA sửa tay không cần đọc code. Seed script đọc file này, không hardcode dữ liệu.
4. **`make reset` chỉ xoá prefix release hiện tại** — bản ghi prefix release cũ là dữ liệu
   di sản cho test tương thích ngược, không đụng. Tài khoản test là hạ tầng — giữ qua các
   release, không xoá theo reset.
5. **Thân 6 lệnh Makefile trỏ vào đây** (`python3 environment/local/seed.py …`) — người
   chạy lệnh không cần biết file nằm đâu. Không thêm lệnh mới ngoài hợp đồng 6 lệnh.

## `local/` — pha P viết gì vào đây

| Artifact | Vai trò |
|---|---|
| `seed.py` (hoặc theo stack thuận tay) | Gọi API tạo tài khoản/bản ghi theo `plan-B1.yaml`; idempotent; có `--reset` xoá prefix hiện tại; có `--dry-run` |
| `plan-B1.yaml` | Dữ liệu mẫu mốc B1 theo persona — nguồn: dữ liệu mẫu trong tài liệu nguồn nếu có (VIPER: `PRD §7`), không có thì tự dựng theo luồng chính của từng persona |
| `.env` | Copy từ `../.env.example` đã điền giá trị (URL, mật khẩu tài khoản test). **Không commit** |
| script phụ (tạo tài khoản, boot thiết bị) | Chỉ khi cần — đừng dựng sẵn "cho đủ bộ" |
