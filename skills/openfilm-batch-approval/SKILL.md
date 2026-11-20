---
name: openfilm-batch-approval
description: "Tương thích LEGACY với nhóm cấp stage v1.10; dự án mới dùng openfilm-macro-bundles M0–M7 để phê duyệt cấp nhiều giai đoạn."
---

# Batch approval — LEGACY v1.10.0, thay bởi macro v1.11.0

**Dự án mới bắt buộc dùng `openfilm-macro-bundles/SKILL.md` và `MACRO_POLICY.json`**. `BUNDLE_POLICY.json`, `bundle_scheduler.py`, `validate_bundle_gate.py` vẫn tồn tại để đọc lại các checkpoint đã duyệt ở v1.10.0, **không** được dùng để đề xuất các nút mới theo mỗi stage hoặc packet. Không yêu cầu duyệt từng Pxx nội bộ. Không tự chuyển event `APPROVE_BUNDLE` cũ thành `APPROVE_MACRO` mới mà không kiểm source hashes và quyết định thật.

Trong v1.11.0, 8 nhóm M0–M7 có thể chứa packet trải qua nhiều Pxx; special actions luôn là sub-bundle riêng. `macro_scheduler.py` chỉ đề xuất phạm vi và chọn packet tiếp, `validate_macro_event.py` chỉ kiểm metadata. User phải click nút thật để duyệt scope, rồi nhiều packet chạy trong cùng lượt High, QC/checkpoint liên tục, cuối lượt có nút tiếp tục cùng macro mà không phải phê duyệt lại. `PRODUCTION_STATUS.json` phải phân biệt QC nội bộ với nghiệm thu của user.

**LEGACY:** nếu đang xử lý một `approvalBundles[]` từ v1.10 có thật, chỉ tiếp tục theo quyền/giới hạn gốc đã cấp; không tự mở rộng sang macro khác. Muốn gộp trạng thái dở, trình một kế hoạch chuyển đổi với phạm vi rõ và user duyệt. Không xóa nội dung đã nghiệm thu, lịch sử approvals, hoặc file nguồn.
