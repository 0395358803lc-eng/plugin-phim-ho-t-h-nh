---
name: openfilm-macro-bundles
description: "Mặc định điều phối Video-hoạt-hình từ v1.11.0 bằng 8 macro-bundle M0–M7, gộp nhiều Pxx và 99 packet kỹ thuật, checkpoint/QC nội bộ, một phê duyệt mỗi nhóm có phạm vi rõ, khôi phục qua nhiều lượt High."
---

# Video-hoạt-hình v1.11.0 — 8 macro-bundle, không duyệt từng packet

**ĐÂY LÀ NGUỒN ĐIỀU PHỐI MẶC ĐỊNH CHO DỰ ÁN MỚI.** Các kỹ năng `openfilm-batch-approval`, `openfilm-high-workpackets`, `openfilm-oneclick-approval`, `openfilm-checkpoint-approval` giữ dữ liệu/phương thức cũ dưới nhãn **LEGACY**; khi chúng mâu thuẫn, tuân thủ skill này, không bắt người dùng bấm sau từng packet hoặc sau mỗi Pxx. **Không xin duyệt riêng từng packet.** 99 mẫu packet vẫn là QC/checkpoint và công việc kỹ thuật ở tầng nội bộ, không phải 99 quyền thao tác người dùng.

## Tám nhóm chính và phạm vi

| Macro | Giai đoạn | Kết quả nghiệm thu cấp nhóm |
|---|---|---|
| **M0** | P00–P06 | Đúng máy/thư mục/workspace, danh mục P05 và OpenFilm CLI/Python/VieNeu runtime có bằng chứng; P00–P05 là cổng chuẩn bị, P06 là stage kỹ thuật |
| **M1** | P07–P09 | Đọc 7 file nguồn, quyết định master/profile, chuẩn FilmData và `film.html` hợp lệ |
| **M2** | P10–P11 | Style Bible, nhân vật, storyboard, asset đủ và license rõ |
| **M3** | P12–P13 | WAV VieNeu-TTS GPU-first đã QC, thời gian phụ đề khớp WAV |
| **M4** | P14–P16 | Các shot 2D/3D có preview OpenFilm CLI, QC frame/continuity đạt |
| **M5** | P17–P18 | Master timeline đã phối âm, smoke MP4 5 giây đã được kiểm |
| **M6** | P19–P20 | Draft hoàn chỉnh, QC20 và danh sách lỗi; sửa vượt scope phải xin duyệt |
| **M7** | P21 | FINAL_MASTER.mp4 và source, audio, phụ đề, FFprobe, xem/nghe và nghiệm thu cuối |

M0 **không tự chọn máy hay đường dẫn**: P00 xác minh thiết bị được người dùng chọn, P01 đường dẫn được người dùng cấp, P02 tạo workspace theo yêu cầu, P03–P05 kiểm kê read-only, rồi P05 dừng để trình cài nếu thiếu. Chỉ chạy P06 khi đủ các cổng P00–P05 có bằng chứng. Không coi phê duyệt cập nhật plugin là cho phép cài hoặc render trên Windows.

## Một lần duyệt mở nhiều Pxx, không vô hạn

1. Đọc `references/MACRO_POLICY.json` (8 nhóm), `openfilm-high-workpackets/references/WORKPACKET_DEFINITIONS.json` (99 checklist) và `references/OPERATIONS.md`. Đọc checkpoint thật `reports/PRODUCTION_STATUS.json`, `reports/WORK_UNIT_INDEX.json` và approval log trong workspace đã được chọn; thiếu thì tạo template trạng thái **sau khi được phép ghi**, không bịa tiến độ.
2. Materialize packet IDs từ 7 tệp kịch bản và manifest đã đọc thật; tên cảnh/thoại/asset, lệnh, đường dẫn, input SHA256 phải là dữ liệu đã xác minh. `macro_scheduler.propose(index,policy)` gom packet thành các `macroBundles` đi qua **nhiều stage Pxx**. Không mặc định chọn một lần duyệt mới nếu không biết được toàn bộ phạm vi; khi thông tin xuất hiện sau bước đọc, đưa thêm plan revision có giới hạn.
3. Trình cho người dùng **một nhóm việc có kết quả rõ**: macro ID, những Pxx liên quan, IDs/scopes, file đầu vào/đầu ra, các lệnh OpenFilm CLI được phép, tác động, checksum, chi phí/rủi ro, quyết định cần chọn. Chỉ bấm `Phê duyệt nhóm Mx` từ host mới ghi approval thật. Nút chỉ gửi **một lượt chat mới** qua `GenUI.issueNewTurn`; plugin không tự chạy ngầm hoặc bấm thay người dùng.
4. Trong macro đã phê duyệt, thực hiện nhiều packet an toàn theo thứ tự và dependencies, tự chạy QC, ghi evidence/sha256, checkpoint atomically, đọc lại. `next_eligible_packet` chặn các stage chưa QC, prompt chèn thêm, hoặc gói đặc biệt chưa được duyệt. **Chạy tiếp tự động *trong lượt hiện hành* khi còn khả năng**, không dừng để xin duyệt từng câu thoại, lệnh look, FFprobe, file JSON hay từng shot trong scope.
5. Pxx **đạt QC nội bộ** được đánh dấu `stageStates[Pxx].status=QC_PASS`, `qcStatus=PASS`, evidence path, macroId; đây **không phải người dùng đã nghiệm thu**. Nếu đưa vào `PRODUCTION_STATUS.json`, dùng `macroInternalGate` chỉ khi có phê duyệt kế hoạch macro thực tế và evidence, tuyệt đối không tự ghi acceptanceApproval APPROVED. Packet `READY_FOR_REVIEW` có bằng chứng/QC là đủ cho packet tiếp theo **cùng macro**, nhưng sang macro khác phải có macro acceptance của người dùng.
6. Nếu kết thúc lượt High khi macro còn dở: giữ planApprovalId, revision, hashes; hiện **Tiếp tục nhóm đã duyệt**. Một lần bấm tiếp tục turn mới, không xin một phê duyệt mới; kiểm đúng máy/workspace, hash, scope, actual file và revision trước lệnh. Nếu dữ liệu nguồn thay đổi, dừng/plan revision mới. Không hứa một lượt High chắc chắn xử lý toàn bộ 8 macro.
7. Khi mọi packet trong macro có artifact/QC thật, hiển thị một nút **Nghiệm thu nhóm & làm nhóm kế** (chỉ khi nhóm kế đã được công khai với scope, không có special action) hoặc **Nghiệm thu nhóm**. Acceptance thực của người dùng cho phép chuyển `READY_FOR_REVIEW` sang `PASS` cho packet và macro, giữ acceptanceApprovalId của macro. Nếu FAIL, dừng phần bị ảnh hưởng, trình nhóm issue và **Phê duyệt sửa trong phạm vi**; không tự sửa source kịch bản đã duyệt.

## Phê duyệt cài đặt và những cổng KHÔNG gộp thành phê duyệt thường

**Mọi `PACKAGE_INSTALL`, `MODEL_DOWNLOAD`, `BROWSER_DOWNLOAD`, `SYSTEM_CHANGE`, `GPU_TO_CPU_FALLBACK`, `VOICE_CLONING`, `EXTERNAL_PROVIDER`, `PAID_ACTION`, `DELETE`, `PUBLISH`, `OUT_OF_SCOPE`** phải lập kế hoạch và phê duyệt đặc biệt **riêng**. `P06.10` OpenFilm E2E first render là special action; không đưa nó vào normal macro chung để tự chạy. OpenFilm CLI A02 là điều kiện bắt buộc; OpenFilm Desktop không làm runtime dự phòng. `npx @latest`/tải âm thầm bị cấm. VieNeu-TTS phải ưu tiên GPU CUDA/PyTorch, CPU/ONNX chỉ được đề xuất nếu GPU không đáp ứng có chứng cứ và phê duyệt riêng. Giọng nói chỉ từ nguồn đã khóa; không âm thầm dùng OpenFilm `get voice` hoặc provider ngoài.

**Các quyết định của con người cũng không được tự suy đoán:** P08 cần profile/style/master đã được người dùng đồng ý (`PROFILE_CHOICE`); trước P11, style/character phải có quyền duyệt (`VISUAL_DIRECTION`); P12 voice preset cần duyệt (`VOICE_CONFIGURATION`); P13 cần nghiệm thu nghe WAV nếu có lời thoại (`VOICE_AUDIO_QC`). Nếu không có thoại, ghi `NO_DIALOGUE_VERIFIED` và bằng chứng để SKIP P12/P13 theo chính sách; không giả lời thoại hay mẫu giọng đã nghe. Nếu connector không chuyển âm thanh, xuất file QC đã xác minh để người dùng tải/gửi lại; dừng ở cổng nghe cần thiết. P21 **bắt buộc người dùng nghiệm thu bản cuối**, dù metadata và QC20 PASS.

## Bằng chứng và UI

- Sử dụng `references/macro_scheduler.py` để **đề xuất** nhóm/packet tiếp; `references/validate_macro_event.py` chỉ kiểm tra metadata, **không** xác thực quyền truy cập thực tế hay thay sự kiện user click. Mỗi lệnh còn phải kiểm phạm vi, shell, an toàn path và host user action. Nút `APPROVE_MACRO`, `RESUME_APPROVED_MACRO`, `ACCEPT_MACRO`, `ACCEPT_AND_APPROVE_NEXT_MACRO`, `APPROVE_MACRO_REPAIR` gửi đúng `macroBundleId`, `packetIds`, `stageIds`, `scopeIds`, `allowedPaths`, `allowedCommands`, `inputHashes`, `stateRevision`, `deviceId`, `workspace` và `filmId`; special đính kèm approval riêng. Nếu không hỗ trợ nút thật, đưa câu phê duyệt một dòng đã điền sẵn, không dùng nút giả.
- Không ghi `PASS` chỉ từ code/fixture/log. OpenFilm `look` phải có ảnh và exitCode; `render` phải có MP4 thực, FFprobe, kiểm xem/nghe, nhất là M5–M7. Đường dẫn phải trong workspace được duyệt, hash tính từ file thật. Không gộp `P05` phê duyệt cài đặt với P21 render cuối.
- Bảo toàn dự án v1.10 đang có: trường `approvalBundles` là lịch sử **LEGACY**, không xóa/migrate tự động. Nếu chuyển workflow đang dở, chỉ lập `macroBundles` cho packet chưa nghiệm thu sau khi kiểm file/hashes và có scope user mới; packet PASS cũ giữ nguyên.

**Nguồn chính sách:** `references/MACRO_POLICY.json`; **quy trình áp dụng:** `references/OPERATIONS.md`; **hợp đồng macro-index:** `references/MACRO_INDEX_TEMPLATE.json`.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate
**Chặn ACCEPT M2/M4/M5/M6/M7**: Dữ liệu `WORK_UNIT_INDEX.visualTargets[Mx]` phải bao gồm danh sách thực toàn bộ storyboard/asset/shot bắt buộc. Tạo ảnh thật theo `openfilm-visual-inspection`; thực sự chuyển ảnh vào ChatGPT vision; ghi nhận xét, ảnh và source hash; lưu `qc/visual/Mx/VISUAL_QC_REPORT.json` sau khi nhìn; kiểm bằng `validate_visual_qc.py --workspace` trên máy đã chọn. Tạo `visualGates[Mx]` (status, reportPath, reportSha256, stateRevision) từ report được xác minh. Nút nghiệm thu phải đính `visualReportSha256` đã công khai cho người dùng. Thiếu hình, chỉ trả metadata, ảnh stale hay thiếu mốc/shot phải BLOCKED, tuyệt đối không nhận diện PASS. **Không tạo thêm nút duyệt mỗi frame/packet**; những việc này nội bộ trong macro, chỉ nút tiếp tục qua lượt High hoặc nút sửa khi thay đổi ngoài phạm vi. M5/M6/M7 phải dùng đúng MP4 smoke/draft/master của chính macro, không dùng frame storyboard/pre-render thay thế.
