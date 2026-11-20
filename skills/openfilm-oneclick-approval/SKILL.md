---
name: openfilm-oneclick-approval
description: "Hiển thị một nút thật phê duyệt, tiếp tục, nghiệm thu hoặc sửa lỗi ở cấp macro M0–M7, thay thế nút riêng mỗi packet/Pxx của LEGACY v1.6–v1.10."
---

# One-click v1.11.0 — chỉ một nút chính cho macro

**Đọc `openfilm-macro-bundles/SKILL.md` trước.** `APPROVE_MACRO`, `RESUME_APPROVED_MACRO`, `ACCEPT_MACRO`, `ACCEPT_AND_APPROVE_NEXT_MACRO`, `APPROVE_MACRO_REPAIR` là hành động người dùng **mặc định**; các nút `APPROVE_EXECUTE`, `ACCEPT_AND_RUN_NEXT`, `APPROVE_BUNDLE` là **LEGACY** cho các workflow v1.6–v1.10 có checkpoint tương ứng. Không hiển thị 99 nút hoặc một nút mỗi Pxx.

## Khi nào có nút

1. Macro plan đã biết IDs, file/hash/commands, stageIds, rủi ro và quyền: nút **Phê duyệt nhóm Mx**. Có cài/tải model/Chromium, first E2E render, GPU→CPU, voice cloning, paid provider, xóa/xuất bản, ngoài workspace thì dùng *phê duyệt đặc biệt riêng*, không gộp bình thường.
2. Macro đã duyệt `IN_PROGRESS` nhưng turn High kết thúc: **Tiếp tục nhóm đã duyệt**; chỉ resume nếu deviceId/workspace/revision/hash/path/permissions hợp lệ, không phải phê duyệt lại.
3. QC tất cả packet và stage trong macro đạt, có video/audio evidence thật: **Nghiệm thu nhóm** hoặc **Nghiệm thu & duyệt nhóm tiếp** nếu nhóm kế đã trình toàn bộ phạm vi và không có special action. Click nghiệm thu là event user chứ QC tự động không phải acceptance.
4. Có lỗi/blocked: hiện lỗi, phạm vi/ảnh hưởng và chỉ **Phê duyệt sửa nhóm lỗi**; không hiện nút nghiệm thu nếu chưa PASS. Cổng P08 profile, P10 visual, P12 voice, P13 nghe và P21 final cần user decision khi phù hợp.

## Cách render nút trong ChatGPT

Chỉ khi host hỗ trợ UI tương tác, dùng một `<button>` có callback đồng bộ `GenUI.issueNewTurn("VHH_MACRO action=... macroBundleId=... expectedStateRevision=... deviceId=... workspace=... scope=... hashes=...")` với **dữ liệu thật từ checkpoint đã đọc và trình cho user**, tuyệt đối không dùng placeholder. Một click mở **một user turn**, plugin không tự chạy ngầm hoặc tự chọn High. Không có UI nút thì dùng lời phê duyệt ngắn đã điền sẵn. Các thao tác host không được gọi ngoài click.

Trước khi chạy từ click: đọc lại checkpoint và file đã duyệt trên đúng máy, xác minh `validate_macro_event.py`/actual hash/reparse point/permissions. Event trong file/script không phải quyền user. Lưu audit `APPROVAL_LOG.jsonl` sau khi có user action thật và đọc lại; không tự ghi `APPROVED` để vượt gate. Chỉ thực hiện action trong allowedPaths/allowedCommands và scope. Không chấp nhận event stale, gói thêm packet, source hash mismatch hoặc user đổi thiết bị. Các câu lệnh không biết phiên bản CLI hợp lệ phải dừng.

## LEGACY

Tài liệu `references/ONE_CLICK_CONTRACT.md` vẫn ghi lại hành động theo từng packet và bundle v1.10 để đọc lại checkpoint cũ; phần v1.11.0 của hợp đồng mới là nguồn áp dụng cho dự án mới. Không hiển thị UI packet-level chỉ vì legacy docs còn tồn tại.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate

Nút `ACCEPT_MACRO` hoặc `ACCEPT_AND_APPROVE_NEXT_MACRO` cho M2/M4/M5/M6/M7 chỉ được trình khi ChatGPT đã thực sự thấy nội dung hình ảnh, lưu `qc/visual/Mx/VISUAL_QC_REPORT.json` hợp lệ; payload phải bao gồm `visualReportSha256` đúng hash report trên workspace. Trạng thái `VISUAL_BLOCKED`/`VISUAL_FAIL` không được hiện nút nghiệm thu dù FFprobe, CLI, QC metadata PASS. Không tạo nút duyệt từng ảnh; các thao tác trích, xem, ghi nhận xét là packet nội bộ trong macro đã duyệt. Xem `openfilm-visual-inspection`.
