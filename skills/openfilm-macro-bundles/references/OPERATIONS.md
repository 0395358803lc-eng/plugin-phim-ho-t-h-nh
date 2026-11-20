# Macro Operations — user approval boundary vs internal QC

## Giao thức chọn lô

P00–P05 phải có chứng cứ `preflightGates[Pxx]` trước P06. `macro_scheduler.propose` sắp đúng thứ tự template từ WORKPACKET_DEFINITIONS, gộp các packet materialized qua những Pxx thuộc cùng M0..M7. Nếu gặp action `specialApprovalRequired` hoặc risk class đặc biệt, bắt buộc tách thành một sub-bundle có cùng macroId nhưng duyệt đặc biệt riêng. Việc chờ người dùng chọn profile, style, voice hoặc nghe giọng tạo `decisionGates` được ghi từ lượt user thật; không tự điền `APPROVED`.

**M0:** Kiểm P00–P05 trước; nếu thiếu CLI/Node/FFmpeg/Chromium, P05 trình cài từng component/source/size/checksum/paths, không tự cài. Phê duyệt cài hoặc render E2E lần đầu là special event. CLI capability P06.12 **trước** P06.09/P06.10. Không gọi CLI ở P04 read-only gây tải ngầm.

**M1:** P07 đọc đủ bảy file → P08 chỉ khi `PROFILE_CHOICE` user đã duyệt → P09 FilmData, bootstrap film.html và validator. Nếu chưa rõ profile, dừng đúng P08 và đưa quyết định ngắn, không giả định user chọn OpenFilm Master khi yêu cầu rõ người dùng cần xác nhận.

**M2:** P10.06 chọn Canvas hoặc file **trước** storyboard; style/character được duyệt trước sinh asset P11. Không phải luôn bật OpenFilm Canvas khi CLI không hỗ trợ.

**M3:** P12 voice preset/backend đã xác minh → GPU WAV+FFprobe → nghe thật khi có thể → P13 phụ đề khi `VOICE_AUDIO_QC` được xác nhận. Không có thoại thì skip có chứng cứ.

**M4:** P14.06 thay placeholder **trước** P14.03/P14.05, dựng 3D P15 chỉ khi có cảnh 3D, P16 OpenFilm CLI look/random seek/continuity sau khi cảnh thật tồn tại.

**M5:** P17.07 hoàn thiện film.html **trước** P17.05/P17.06; sau đó P18 render smoke 5s + FFprobe/QC trong cùng macro đã duyệt, nhưng không gộp quyền tải/chi phí mới.

**M6:** P19 draft và P20 QC20; nếu phát hiện lỗi, dừng phần phụ thuộc, nhóm issue cùng nguyên nhân, trình phạm vi sửa; không tự công nhận sửa một cảnh là đã QC toàn phim.

**M7:** P21 render master + probe + final view/listen + source manifest, vẫn cần quyết định nghiệm thu cuối cùng. Không công bố MP4 khi file không thực sự tồn tại.

## Selector & state transition

- `macroBundles` giữ trạng thái nhóm; `packets[]` vẫn giữ checklist chi tiết và các hashes; `stageStates[Pxx]` lưu QC nội bộ. `PRODUCTION_STATUS.json` duy trì schema legacy 1, thêm `macroInternalGate` chỉ với nguồn planApproval macro thật, evidence được kiểm và không gán nhãn user acceptance.
- `next_eligible_packet(index, macroBundleId, policy)` trả packet ID hoặc None. Không thực thi bất kỳ lệnh nào. Trong một macro, trước khi chọn packet thuộc stage sau phải có QC stage trước và decision gates; cross-macro phải có acceptance user và packet PASS hợp lệ. Ngay trong một stage cũng không vượt packet đứng trước ở template order. Không bỏ qua `FAIL/BLOCKED/INVALIDATED`.
- Một sub-bundle special là một hành động cần phê duyệt đặc biệt. Sau khi hoàn tất special và có user acceptance, phần còn lại của cùng macroId mới được chạy. Không coi `APPROVE_MACRO` thường cho phép `specialApprovalRequired`.
- `validate_macro_event.py` kiểm exact scope/hashes/command/stage/revision; bản thân metadata validator không kiểm được file thật, người bấm thật, license hay chất lượng video. Trước mỗi thao tác hãy đọc lại state và file/sha thực, kiểm reparse point, khóa PATH, quyền workspace rồi mới thực thi.

## Nút sau mỗi lần làm việc

**Sau khi được duyệt**: chạy liên tiếp các việc nhỏ đã nằm trong scope trong chính turn; nếu High hết lượt, chỉ hiện `Tiếp tục nhóm đã duyệt` không xin duyệt kế hoạch lại. **Sau khi nhóm đủ QC**: hiện `Nghiệm thu nhóm` hoặc `Nghiệm thu & phê duyệt nhóm kế` với phạm vi cụ thể nếu không có hành động đặc biệt. **Khi lỗi/blocker**: hiện một nút `Phê duyệt sửa nhóm lỗi` hoặc trình quyết định cần thiết; không hiện `PASS`/`Nghiệm thu` thiếu bằng chứng. Plugin skills-only không thể tự tạo nhiều lượt chat hoặc click nút thay người dùng.

## Giới hạn bắt buộc

Không cấp sẵn quyền cho IDs và file chưa được materialize, không lấy mô tả 7 file trong ảnh thay nội dung thực, không giả sourceHash, không dùng branch CLI Desktop fallback, không tự cài/TTS fallback/đăng video. Nếu manifest chưa xác định đủ lô dài, chỉ công bố phạm vi đã biết rồi mở rộng bằng plan mới sau khi kiểm chứng; đừng tạo chuỗi các nút vô nghĩa chỉ để xem file hoặc chạy probe.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate
Với M2/M4/M5/M6/M7, sau technical QC nhưng **trước** event nghiệm thu, phải có `visualTargets`, report từ ảnh đã được ChatGPT thật sự thấy, hash nội dung, trạng thái `VISUAL_PASS`. `validate_macro_event.py` đọc và kiểm byte của report, PNG, nguồn scene hoặc MP4. Giới hạn: Python không chứng minh agent đã thật nhìn thấy ảnh, vì vậy mọi field `imageActuallyReceived` và `hostImageEvidence` phải được ghi sau công cụ multimodal thực. Không có image content ở turn → `VISUAL_BLOCKED`. Sau mỗi sửa scene/render mới, vô hiệu report có source hash cũ; xem lại ảnh mới. Không nhầm xem frame với xem liên tục MP4 hoặc QC âm thanh. Không sinh approval mới cho mỗi ảnh.
