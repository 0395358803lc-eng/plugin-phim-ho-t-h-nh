---
name: openfilm-high-workpackets
description: "Dùng 99 packet nhỏ để chia việc và QC/checkpoint nội bộ nhưng điều phối thực thi theo 8 macro M0–M7 cho dự án Video-hoạt-hình mới."
---

# High work packets v1.11.0 — QC nội bộ, **không phải nút duyệt**

**Mặc định** phải đọc `openfilm-macro-bundles/SKILL.md` và `references/WORKPACKET_DEFINITIONS.json` trước tiên. 99 mẫu vẫn giữ nguyên ID và chức năng, nhưng `requiresExplicitApproval=false` ở packet bình thường và `approvalMode=INHERIT_MACRO`. Chỉ packet `SPECIAL_SEPARATE` đòi phê duyệt đặc biệt. Mọi chính sách một packet/một click đời cũ được coi là **LEGACY** cho checkpoint v1.6–v1.10, không dùng cho dự án mới.

- Phân giải mỗi template từ ID thực xác minh: shot/dialogue/asset/source/issue/render. Chưa biết ID/file thì báo NEEDS_INPUT, không tạo giả. Nguồn 7 tệp kịch bản gốc bất biến. Đường dẫn workspace relative + SHA256 thật.
- Trong **một macro user duyệt**, thực hiện nhiều packet liên tiếp khi cùng scope/permissions và QC trước đó PASS; không dừng sau từng packet. `READY_FOR_REVIEW + qcStatus=PASS` là đủ cho dependency **cùng macro**; chưa phải người dùng nghiệm thu. Sang macro khác yêu cầu macro trước được người dùng ACCEPT và packet PASS hợp lệ.
- Phân chia kỹ thuật hữu ích: P09 1–2 shot hoặc tối đa 4 dialogue/packet; P10 1 shot; P11 1 asset; P12 ≤3 câu thoại ngắn/packet GPU, nhưng macro có thể chạy nhiều packet; P14–P16 1 shot/packet; P18 smoke render/probe/listen trong M5; P21 render/probe/handoff trong M7. Nếu phức tạp, chia thêm *packet nội bộ* không sinh thêm nút.
- Sau **mỗi packet** phải ghi checkpoint/hash/QC trong workspace khi được phép. Nếu FAIL/BLOCKED dừng các phụ thuộc và trình sửa ở cấp issue/scope; không tự chấp nhận QA sáng tạo. Khi hết lượt High trả `RESUME_APPROVED_MACRO` để mở turn mới theo phê duyệt trước, không yêu cầu user nhập prompt hay phê duyệt lại.
- P06 CLI first, VieNeu CUDA/PyTorch GPU-first. Không âm thầm fallback CPU/ONNX, tải model/Chromium, chi phí hoặc gọi provider ngoài. M0 phải qua P00–P05 trước; M7 phải có MP4 thật và người dùng nghiệm thu.

## LEGACY (chỉ đọc state cũ)

`openfilm-batch-approval` cùng `ONE_CLICK_CONTRACT.md` chứa lịch sử một bundle mỗi stage và packet-level actions. Không xóa lịch sử `approvalBundles[]`; quy trình mới dùng `macroBundles[]`, `MACRO_POLICY.json`, `macro_scheduler.py` và `validate_macro_event.py`. Trong trường hợp chưa được phép chuyển workflow, dừng/đề xuất kế hoạch, không âm thầm sửa trạng thái.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate
M2/M4/M5/M6/M7 thêm công việc **trích ảnh thật → nhận ảnh trong ChatGPT vision → nhận xét từng shot/role → lưu Visual QC → sửa & nhìn lại** làm packet nội bộ trong cùng macro; **không thêm nút từng frame/packet**. Không tự ghi `VISUAL_PASS` chỉ từ file tồn tại/FFprobe, thiếu image input thì BLOCKED. Giữ 99 template IDs; các packet có `visualEvidenceRequired` gọi skill `openfilm-visual-inspection`.
