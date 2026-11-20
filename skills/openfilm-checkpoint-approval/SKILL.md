---
name: openfilm-checkpoint-approval
description: "Bảo toàn checkpoint và QC theo packet/Pxx nhưng nghiệm thu ở cấp macro M0–M7; hỗ trợ khôi phục lô đã duyệt, chặn nghiệm thu giả và quy trình LEGACY."
---

# Checkpoint và nghiệm thu v1.11.0 — macro user approval, packet nội bộ

**Nguồn điều phối mặc định:** `openfilm-macro-bundles/SKILL.md`. Không nhầm QC PASS với người dùng phê duyệt. 99 packet là chứng cứ kỹ thuật, không có nút sau mỗi packet hoặc stage. **LEGACY:** `STATE_CONTRACT.md`, `PRODUCTION_STATUS_TEMPLATE.json` và `approvalBundles[]` giữ tương thích các hồ sơ v1.10, không được tự đánh dấu lại nghiệm thu.

## File trạng thái có thật trên workspace

- `reports/PRODUCTION_STATUS.json`: 16 stage P06–P21, QC/evidence, status và workUnits; `macroInternalGate` là marker **QC nội bộ** khi có planApprovalId macro thật. Không được ghi `acceptanceApproval.status=APPROVED` khi user mới chỉ duyệt kế hoạch macro.
- `reports/WORK_UNIT_INDEX.json`: `packets[]`, `macroBundles[]`, `approvalBundles[]` (**LEGACY**), `stageStates{}`, `preflightGates{}`, `decisionGates{}`, stateRevision, deviceId, workspace, filmId. Giữ nguyên packet IDs/checkpoints đã QC; không chạy lại PASS nếu hashes còn đúng.
- `reports/APPROVAL_LOG.jsonl`: ghi các sự kiện user click thật + đúng scope, không bịa approval. Ghi state atomic và đọc lại sau mỗi packet đã thực hiện trên máy cho phép; nếu không có quyền ghi báo BLOCKED.

## Transition

Một packet bình thường thuộc macro đã duyệt: `PLANNED → IN_PROGRESS → READY_FOR_REVIEW` khi QC/evidence có thật. Dependency packet **trong cùng macro** có thể tiếp tục trên `READY_FOR_REVIEW qcStatus=PASS`, sau khi stage trước trong macro đã `QC_PASS` và các decision gates cần thiết được xác nhận. Không được tự chuyển packet thành `PASS` chỉ vì QC. Khi user nghiệm thu macro với evidence thật, các packet được gắn `acceptanceApprovalId` của macro và chuyển `PASS`, macro chuyển `PASS`. Để chuyển sang macro khác: macro trước phải có acceptanceApprovalId; special packet giữa chừng cần phê duyệt riêng.

Giai đoạn Pxx có thể `PASS` theo kỹ thuật **chỉ khi** có `macroInternalGate` hợp lệ/approved plan/evidence (validator `validate_production_state.py`), không được gọi là *user acceptance*. Stage P21 dù QC đạt vẫn đòi người dùng nghiệm thu final; không tự `PASS` bằng marker nội bộ. Các stage `SKIPPED` chỉ khi được policy cho phép, ghi lý do/evidence, không fake hoàn thành.

## Điều kiện dừng

Dừng theo lỗi thật, kết quả chưa nghe/nhìn, thiếu chứng cứ file, ngoại phạm vi, hash hoặc revision thay đổi, gói đặc biệt chưa duyệt, runtime OpenFilm CLI chưa được chứng minh, hoặc VieNeu GPU chưa đạt. Nếu hết lượt High khi vẫn đang trong macro, lưu điểm dừng, hiện **Tiếp tục nhóm đã duyệt** (không đòi duyệt lại) với event host thật. Nếu nguồn thay đổi hoặc scope mới, trình replan minh bạch. Chỉ invalidation các packet + downstream liên quan, không xóa hay ghi đè bừa.

## Trình xác thực

`validate_production_state.py` đọc schema cũ và marker macro khi có; `validate_work_packets.py` đọc cả `approvalBundles` LEGACY và `macroBundles` mới; `openfilm-macro-bundles/references/validate_macro_event.py` kiểm callback metadata. Đọc/so file SHA256 trên máy đã cấp quyền trước khi thực thi/nhận nghiệm thu, không coi validator metadata là giấy phép chạy.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate
Khi nghiệm thu macro M2/M4/M5/M6/M7, ngoài QC kỹ thuật, yêu cầu `visualTargets[Mx]` và `visualGates[Mx]` trỏ `qc/visual/Mx/VISUAL_QC_REPORT.json` có ảnh **đã thực sự xem qua công cụ multimodal** và hash của ảnh/nguồn. Thay sourceHash/render revision hoặc sửa shot → invalidate visual report, không dùng report cũ. Metadata validator không xác nhận mắt mô hình; phải thấy image content ở lượt thật. Không tạo nút duyệt cho từng ảnh.
