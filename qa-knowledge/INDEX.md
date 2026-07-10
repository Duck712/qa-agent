# QA Knowledge Base — mục lục
> Agent: đọc file này đầu tiên. Làm việc với đối tượng nào → mở đúng file đó, đối chiếu từng mục.

## Checklists (đối tượng cụ thể)
- checklists/form-input.md — test mọi form nhập liệu (field, validate, submit)
- checklists/auth-login.md — đăng nhập / session / phân quyền
- checklists/file-upload.md — upload file, media, ảnh
- checklists/api-common.md — test API bất kỳ (contract, pagination, method, rate limit, versioning, CORS, encoding)
- checklists/abnormal.md — case bất thường cross-cutting (network, race, timezone, browser edge, mobile, session mid-flow, cache/stale, data volume, i18n, recovery)

## Skills (tư duy / kỹ thuật)
- skills/tester-techniques.md — kỹ thuật thiết kế test case (boundary, equivalence, decision table, state transition, exploratory, viết bug tốt)
- skills/test-lead-judgement.md — tư duy ra quyết định (ưu tiên, cắt phạm vi, GO/NO-GO, viết report)

## Bug patterns & lessons
- bug-patterns.md — lỗi dev hay mắc, soi trước khi test
- lessons/ — bài học sau từng round (agent đề xuất §7g Tầng 1, user duyệt Tầng 2 mới push vào checklists/bug-patterns)

## Security testing
Security case NẶNG (active verification OWASP Top 10, CVE, secrets, supply-chain) KHÔNG thuộc kho này — thuộc agent riêng `qa-security-agent` (xem `.claude/agents/qa-security-agent.md`). Kho này chỉ giữ security case cơ bản trong `auth-login.md §3` (authz, IDOR, tenant isolation) và `form-input.md §2` (XSS/SQLi basic).
