# Target `library` — thư viện, SDK, plugin

## Chạy bằng gì
Một **chương trình dùng thử** ở `qa/sandbox/<run-id>/consumer/`, cài gói **từ nơi phát hành** (registry, tarball,
wheel được giao — version ở `QA.md §Target`), không import thẳng từ thư mục code nguồn (sẽ bỏ sót lỗi đóng gói).

```bash
S=qa/sandbox/$RUN/consumer; mkdir -p $S && cd $S
# JS:     npm init -y >/dev/null && npm i <goi>@<version>
# Python: python3 -m venv .venv && .venv/bin/pip install <goi>==<version>
# Java:   pom/gradle tối thiểu phụ thuộc <group:artifact:version>
```
Mỗi TC một file ví dụ (`tc-xxx-001.mjs` / `.py`) viết theo **tài liệu công khai** — tài liệu nói gì, dùng đúng thế.

## Công thức
- **Đóng gói**: cài sạch được · import/require được theo cả cách tài liệu nêu (ESM/CJS, sub-path) · có type (`.d.ts`, `py.typed`) nếu hứa · không kéo phụ thuộc thừa/nặng bất thường.
- **API công khai**: mỗi hàm/lớp trong tài liệu chạy đúng ví dụ tài liệu (ví dụ trong README chạy được là TC rẻ nhất).
- **Lỗi**: đầu vào sai → ném lỗi đúng loại, thông điệp rõ; không nuốt lỗi; không `process.exit`/`sys.exit` trong thư viện.
- **Biên**: null/undefined/None, chuỗi rỗng, số rất lớn, unicode, danh sách rỗng, đầu vào rất lớn.
- **Tương thích**: các runtime/version trong phạm vi (Node 18/20/22, Python 3.9–3.13) · nâng từ version trước theo changelog, có breaking change không khai.
- **Đồng thời / tài nguyên**: gọi song song, dùng lại client, đóng kết nối, rò bộ nhớ trong vòng lặp dài (đo thô).
- **SDK gọi dịch vụ**: timeout, retry, lỗi mạng, xác thực sai, phân trang — kết hợp công thức `api.md`.
- **Bảo mật cơ bản** (khi được phép): `npm audit` / `pip-audit` trên consumer, secret không bị log.

## Bằng chứng tối thiểu
File chương trình dùng thử + lệnh chạy + stdout/stderr/exit code + version gói đã cài (`npm ls <goi>` / `pip show <goi>`) + version runtime.
