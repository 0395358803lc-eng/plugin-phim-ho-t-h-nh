# Công thức khôi phục High packets

1. Xác minh máy, `PROJECT_DIR`, workspace P00–P02; kiểm tra P03–P05 hoặc bản report đã được nghiệm thu còn hiệu lực.
2. Đọc 7 file nguồn và hash; đọc `PRODUCTION_STATUS.json`, `WORK_UNIT_INDEX.json`, `APPROVAL_LOG.jsonl` nếu đã có.
3. Validate bằng `validate_production_state.py` và `validate_work_packets.py`; kiểm chứng file/hash thực và tất cả IDs có thực.
4. Chọn bundle đầu tiên có scope được duyệt, các packet con theo dependency/status, không thực hiện nếu `READY_FOR_REVIEW` đang đợi người dùng bấm nghiệm thu, hoặc `WAITING_APPROVAL` chưa click.
5. Liệt kê bundle + scope + expected outputs + QC. Chỉ sau phê duyệt mới chạy **nhiều packet con** trong đúng bundle, lưu checkpoint/QC từng packet.
6. Sau chạy: lưu báo cáo QC từng packet, checkpoint atomic+readback, không tự chuyển thành PASS user acceptance; chỉ hiển thị nút ở cấp bundle.

Các tệp template là **kế hoạch có thể thực hiện khi có quyền máy**, không phải các bước đã thực thi. Mỗi câu bấm là user turn mới. Khi token/timeout sát giới hạn, dừng tại checkpoint và đề xuất packet nhỏ hơn, không hứa tiếp tục ngầm.

**Ưu tiên v1.11.0:** `openfilm-macro-bundles/SKILL.md` và `MACRO_POLICY.json` ghi đè cả lịch sử packet-level lẫn stage-only bundle v1.10.0; nhóm xuyên Pxx, QC/checkpoint từng packet nhưng user chỉ duyệt macro, special action riêng.
