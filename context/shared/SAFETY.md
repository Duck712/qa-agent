---
type: safety
tier: T1
last_reviewed: "{{DATE}}"
---

# SAFETY — {{PROJECT_NAME}}

> **Luật an toàn khi test trên PRODUCTION hoặc STAGING** (dòng `Môi trường:` của manifest) —
> mục 1–5 áp cho cả hai, mục 6 thêm riêng cho staging. Bản thao tác của `SPEC.md §7`, cụ thể hoá
> theo sản phẩm ở pha S/P (nguồn: `TEST-STRATEGY §8` + `ENVIRONMENT.md`). Phanh thật là
> CÁCH LY, không phải permission rule. Vi phạm mục 4 là ngoại lệ "hỏi thật" của luật #2 —
> dừng và hỏi QC, không tự quyết.

---

## 1. Chỉ đứng trong vùng test

- Mọi thao tác bằng tài khoản test ở `ENVIRONMENT.md §3`, trong tenant test ở `§4`.
- Mọi bản ghi tạo ra mang prefix `SPEC-r<N>-` ở trường nhận diện.
- **Không ghi/sửa/xoá bản ghi thiếu prefix** — kể cả "để thử xem sao". Đọc thấy dữ liệu người thật (lỗ cách ly) thì đó là bug S1, chụp bằng chứng (che dữ liệu cá nhân) và dừng tay ở đó.
- Staging dùng chung với dev/QA khác: bản ghi không mang prefix SPEC là của người khác — đụng vào là phá việc của họ.

## 2. Dữ liệu

- Seed và dọn **qua API** bằng tài khoản test — `make seed` / `make reset`.
- `make reset` chỉ xoá prefix release hiện tại; **dữ liệu di sản** release cũ giữ lại cho test tương thích.
- Thứ không xoá được qua API → ghi `ENVIRONMENT.md §7 Rác còn lại`, không cố xoá đường khác.
- Không dùng dữ liệu người dùng thật làm dữ liệu test — kể cả copy ra.

## 3. Hướng ra ngoài

- TC bắn email/SMS/notification → địa chỉ nhận phải thuộc SPEC (hộp thư test ở `ENVIRONMENT.md`). Không có hộp test → TC đó `BLOCKED` + lỗ hổng ghi HANDOVER, không "thử đại" vào số/địa chỉ thật.
- Thanh toán chỉ trong sandbox. Không có sandbox → `BLOCKED`, hỏi QC.
- Webhook hai chiều: đầu nhận thử là endpoint của SPEC, không trỏ hệ thống thật của bên thứ ba.

## 4. CẤM — chạm là dừng hỏi QC

| Cấm | Vì sao |
|---|---|
| Chạm thẳng DB production (`psql`/`mysql`/… — lớp `ask` chặn sẵn) | SPEC là client, không phải admin; một câu UPDATE nhầm là phá dữ liệu người thật không thu hồi được |
| Xoá/sửa dữ liệu ngoài tenant test | Như trên |
| Stress/load nặng lên production | Đánh sập môi trường người thật đang dùng; cần load test → `TEST-STRATEGY §7` khai môi trường riêng, QC quyết |
| Gửi thông báo tới người thật · tiêu tiền thật | Hướng ra ngoài, không thu hồi được |
| Ghi vào repo nguồn (hook `guard_readonly` chặn sẵn) | Đầu vào chỉ đọc — luật #4 |
| Active scan / payload bảo mật khi chưa có xác nhận quyền kiểm thử (DECISIONS dẫn nguyên văn QC) | Thử tấn công hệ thống không được phép là vi phạm, kể cả trên staging |
| Payload phá hoại (`DROP`/`DELETE`/`rm`, DoS thật) | Chỉ CHỨNG MINH lỗ (`SELECT`, `id`/`whoami`), không khai thác phá |

## 5. Nhịp độ (production và staging dùng chung)

- Lệnh gọi lặp (đo hiệu năng, thử rate limit) giãn cách ≥1s, n ≤ 20 mỗi phép đo.
- Thử rate limit dừng ngay khi thấy 429 — mục tiêu là xác nhận CÓ chặn, không phải đo sức chịu. Tài khoản test bị khoá sau khi thử → mở lại (cleanup), ghi vào bằng chứng.
- Đợt phá (breaker/authz/cross/security) chạy **cuối cùng** và dọn ngay sau đợt.

## 6. Thêm cho staging

- **Không nhầm môi trường**: trước đợt 0 so URL thật đang gọi với `ENVIRONMENT.md §1–§2`; host trông giống production (không có `staging`/`stg`/`dev`/`test`/`uat`, hoặc trùng URL production ghi ở `ARCHITECTURE`) → dừng, hỏi QC.
- **Dịch vụ ngoài phải là sandbox**: SMS/email/push/thanh toán của staging hay nối thẳng nhà cung cấp thật. Chưa xác nhận là sandbox (TEST-STRATEGY §8) → TC chạm vào là `BLOCKED`, không "thử đại".
- **Seed thẳng DB staging** chỉ khi `TEST-STRATEGY §8` khai cho phép (QC chốt) — mặc định vẫn qua API. Lệnh DB vẫn qua lớp `ask`.
- Staging bị dev deploy lại giữa chừng → ghi mốc giờ vào RUNLOG §Nhật ký đợt; TC chạy trước/sau không cùng bản, kết quả lệch thì chạy lại trên bản mới.
