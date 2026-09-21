# {{PROJECT_NAME}} — hợp đồng lệnh môi trường test SPEC
#
# Sáu lệnh dưới đây là giao diện chung của quy trình. gate.py và các slash command chỉ gọi
# các lệnh này, không cần biết bên dưới seed bằng Python hay gì khác.
#
# Pha P: viết thân lệnh, trỏ vào environment/local/ (xem environment/README.md).
# Giữ nguyên TÊN target — đổi tên là phá hợp đồng, gate.py sẽ không kiểm được.
#
# Nguyên tắc (SPEC.md §4, §7):
#   seed/reset đi QUA API bằng tài khoản test — CẤM chạm thẳng DB production
#   (staging: chỉ seed DB trực tiếp khi TEST-STRATEGY khai cho phép, QC quyết)
#   reset chỉ xoá bản ghi prefix SPEC-r<N>- của release hiện tại (dữ liệu di sản giữ lại)
#   doctor ở `Môi trường: staging` cảnh báo nếu URL trông như production
#   devices boot đúng MỘT thiết bị và cài bản build từ manifest (checksum phải khớp)

.PHONY: help doctor seed reset accounts devices smoke gate review

PYTHON ?= python3

help:
	@echo "{{PROJECT_NAME}} — SPEC"
	@echo ""
	@echo "  make doctor    kiểm môi trường test: URL 200, tài khoản đăng nhập được, cách ly đúng, env đủ"
	@echo "  make seed      bơm dữ liệu mẫu vào tenant test về mốc B1 (qua API)"
	@echo "  make reset     dọn tenant test về mốc B0 (chỉ xoá prefix release hiện tại)"
	@echo "  make accounts  tạo + thử đăng nhập tài khoản test cho từng vai"
	@echo "  make devices   boot 1 simulator/emulator + cài build từ manifest + kiểm checksum"
	@echo "  make smoke     đi nhanh một luồng lõi trên môi trường test (manifest: Môi trường) bằng tài khoản test"
	@echo ""
	@echo "  make gate      kiểm gate của pha hiện tại (hoặc: make gate P=S)"
	@echo "  make review    pha P: máy soát bộ TC (scripts/review_tc.py)"

define NOT_IMPLEMENTED
	@echo ""
	@echo "  ✗ 'make $@' chưa được hiện thực."
	@echo ""
	@echo "  Pha P chưa xong. Viết thân lệnh trỏ vào environment/local/"
	@echo "  (xem environment/README.md và /spec-prepare)."
	@echo ""
	@exit 1
endef

doctor:
	$(NOT_IMPLEMENTED)

seed:
	$(NOT_IMPLEMENTED)

reset:
	$(NOT_IMPLEMENTED)

accounts:
	$(NOT_IMPLEMENTED)

devices:
	$(NOT_IMPLEMENTED)

smoke:
	$(NOT_IMPLEMENTED)

# --- không đổi ---

gate:
	@$(PYTHON) scripts/gate.py $(P)

review:
	@$(PYTHON) scripts/review_tc.py
