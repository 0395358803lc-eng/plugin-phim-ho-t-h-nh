# P06–P21: đặc tả giai đoạn, đơn vị làm việc, nghiệm thu

**Điều kiện trước:** hoàn tất P00–P05, đã chốt máy/deviceId + `PROJECT_DIR` và `WORKSPACE`, có báo cáo môi trường thực; P05 không tự cấp quyền cài hoặc chạy production. Người dùng có thể đã đặt một thư mục chứa 7 file kịch bản bên trong `WORKSPACE`; gọi đó là `SOURCE_DIR`, **phát hiện thực tế chứ không tự tạo dữ liệu nguồn**.

Mỗi giai đoạn báo `{mã, scope/approval, công việc, đơn vị, đường dẫn đầu ra, QC evidence, PASS/FAIL/BLOCKED/SKIPPED, next action}`. Từng work unit cũng có checkpoint. Trình danh mục trước khi làm; công việc có thay đổi hệ thống, cài gói, tạo media/render cần phê duyệt công đoạn cụ thể. Không có quyền tiếp tục mà người dùng chưa xác nhận.

## Các giai đoạn

| ID | Input và bước công việc nhỏ | Output dự kiến (chỉ ghi có nếu file thật) | Nghiệm thu và điều kiện chặn |
|---|---|---|---|
| **P06 — Nghiệm thu môi trường** | Đọc P05; theo từng ID cần cài, xác nhận phạm vi/phiên bản/path/nguồn và quyền duyệt; dùng lại bản hợp lệ; kiểm thử từng runtime sau cài | `reports/ENV_ACCEPTANCE.md`, `reports/INSTALLED_COMPONENTS.json` | Test version/path/chức năng của mỗi ID; không có ID cần cài → SKIPPED với bằng chứng; thiếu duyệt → BLOCKED |
| **P07 — Kiểm kê 7 tệp** | Xác định `SOURCE_DIR`; mở từng file, kiểm tra UTF-8 BOM/CSV dialect/header/timecode; hash source; so sánh kịch bản tổng ↔ plot/characters/dialogue/scenes/audio/QC cũ | `reports/INPUT_AUDIT.md`, `reports/SOURCE_FILES_MANIFEST.json` | Đủ 7 file thực, CSV parse được, mâu thuẫn/thiếu được đánh dấu; không sửa source âm thầm; không coi `BAO_CAO_NGHIEM_THU.md` là QC video |
| **P08 — Chốt production profile** | Từ shot list/brief, đề xuất 2D/3D, tỉ lệ, FPS, master OpenFilm hay Remotion, license và khả năng hardware; người dùng xác nhận | `reports/PRODUCTION_PROFILE.json` | Engine ghi rõ; nếu Remotion thì kiểm B03,B05–B10 & license trước khi dùng; khối 3D chỉ bật nếu cần |
| **P09 — FilmData** | Map từng row CSV sang stable shot_id; map thoại, speaker, tài sản, thời gian frame; quy tắc [start,end) và rounding; validate JSON | `projects/<film-id>/scene-data/{film.json,shots.json,dialogues.json,assets-manifest.json}` | Không trùng ID/overlap sai, dữ liệu lời thoại khớp cảnh; timing chưa có WAV = estimated/PENDING_AUDIO |
| **P10 — Thiết kế hình** | Đọc `NHAN_VAT.md`, chỉ dẫn hình/âm; tạo style bible, từng character bible, storyboard shot với camera/mood/màu; xin duyệt | `storyboard/`, `character-bible.md`, `style-bible.md` | Quan sát/duyệt tính nhất quán nhân vật, framing, màu, style; không gọi PASS nếu storyboard chưa xem |
| **P11 — Asset production** | Kiểm kê asset user có, reuse nguồn có license, phân hoạch asset_id; tạo SVG, background, GLB/texture/font cần thiết; kiểm tra resolution/paths | `assets/` + manifest hash/license/path | Hình không thiếu, độ phân giải an toàn; không tự gọi API trả phí, không giả asset/model đã sinh |
| **P12 — VieNeu-TTS** | Parse `LOI_THOAI.md` theo dialogue_id/nhân vật; chọn giọng preset sau duyệt; chuẩn hóa script_spoken; sinh WAV từng take trong vùng đã duyệt; nghe QC | `assets/audio/voice/<shot>_<speaker>_<line>_takeNN.wav`, voice manifest, file nghe | FFprobe duration/sample rate, phát âm và sắc thái nghe thật; thiếu voice hoặc không nghe được → BLOCKED; không thoại → SKIPPED có lý do |
| **P13 — Khóa timing & subtitle** | Đo độ dài WAV đã chấp nhận; cập nhật dialogue endFrame/shot khi được duyệt; align VTT/SRT từ bằng chứng, không ước chừng từ số ký tự | `scene-data/film.json` revision mới, `subtitles/*.srt|*.vtt`, `qc/AUDIO_SYNC.md` | Không overlap trái ý, subtitle font tiếng Việt đúng dấu, cue căn được với WAV; trường hợp không lời thoại xử lý theo brief |
| **P14 — Hoạt hình 2D** | Chọn 1–3 shot/lượt, dựng HTML/CSS/SVG/GSAP hoặc React theo master; paused GSAP `seek(t)`/frame-based, no stateful incremental motion | `openfilm/scenes/*.html` hoặc `remotion/src/scenes/*.tsx`, contact sheet, test log | Seek random/frame đầu-giữa-cuối không nhảy, bố cục & hiệu ứng nhất quán; QC theo shot; 2D không có → SKIPPED có lý do |
| **P15 — Cảnh 3D** | Theo shot có 3D, tạo/kiểm camera, model, ánh sáng, WebGL/ANGLE khi Remotion; frame-derived transform, texture cache; giới hạn RAM/VRAM | scene 3D, preview, WebGL log | Không frame đen, model/texture thiếu, camera cắt nhân vật; không có cảnh 3D → SKIPPED, không yêu cầu cài R3F |
| **P16 — Preview/OpenFilm previs** | Dựng preview từng shot/cut, so với storyboard và hướng dẫn góc máy; xem đầu/giữa/cuối, continuity, random seek; file previs nếu được duyệt | `renders/previs/`, `qc/SHOT_PREVIEW_REPORT.md` | Từng shot PASS có screenshot/file; thiếu render engine không ghi PASS |
| **P17 — Lắp ráp timeline** | Import các cảnh hợp lệ vào engine master; thoại, phụ đề, music/SFX, ducking, color, transitions; hash và backup trước sửa project | OpenFilm `film.html` hoặc Remotion composition/sequence, `qc/MASTER_TIMELINE.md` | Track id, duration, sync và license; không trùng audio, không lấy absolute Windows path vào Remotion `staticFile` |
| **P18 — Smoke 5 giây** | Render đoạn gồm motion/âm thanh/phụ đề, 3D nếu có, trong profile đã duyệt; xem/nghe, FFprobe codec/FPS/sample rate | `renders/smoke/smoke-5s.mp4`, `qc/SMOKE_REPORT.md` | MP4 có thật, phát có hình và tiếng nếu brief cần; fail → chặn P19 |
| **P19 — Draft toàn phim** | Chọn profile/concurrency sau kiểm phần cứng; render toàn bộ hoặc theo phần; merge chỉ khi timestamps/codec tương thích; không thay output cũ đã duyệt | `renders/draft/draft-v01.mp4`, log, metadata | Thời lượng/kích thước/FPS đúng profile, đủ shot & âm thanh; chưa xem toàn phim không coi đạt QC cuối |
| **P20 — QC20 và sửa lỗi** | Soát 20 điều kiện; lỗi có `issue_id`, severity, `shot_id`, evidence, plan sửa, ảnh hưởng phụ thuộc; xin duyệt sửa từng scope; re-render unit/cảnh bị ảnh hưởng | `qc/QC20_REPORT.md`, `qc/issues.json`, `renders/draft/draft-vNN.mp4` nếu cần | Chỉ PASS khi 20 điều kiện bắt buộc PASS hoặc ghi ngoại lệ người dùng duyệt rõ; FAIL/BLOCKED chặn P21 |
| **P21 — Master & bàn giao** | Sau QC20 PASS, duyệt render final; xuất MP4 master + SRT/VTT và manifest/source/WAV/log; FFprobe và xem-nghe final | `renders/master/FINAL_MASTER.mp4`, `subtitles/`, `reports/FINAL_ACCEPTANCE.md` | Đảm bảo thật sự có file phát được, mã hóa & duration theo profile; không công bố xuất xong nếu video chưa kiểm chứng |

## Phê duyệt và báo cáo

Mỗi công đoạn cần (1) **duyệt kế hoạch** trước thao tác có ghi/tạo/render/cài; (2) **nghiệm thu output** khi đã có bằng chứng; (3) **duyệt sửa lỗi** khi có FAIL. Quyết định cần ghi `phase_id`, `work_unit_id` hoặc `issue_id`, mô tả scope, người duyệt qua chat/host, thời điểm và bằng chứng đã duyệt. Không trộn duyệt tải model với duyệt voice cloning, tạo media, render hay public video.

Mẫu báo cáo kết thúc mỗi bước:

```text
[P14: HOẠT HÌNH 2D]  BATCH: C001–C003
Đã thực hiện: 3 shot | PASS: 2 | FAIL: 1 | BLOCKED: 0
Bằng chứng: qc/P14/C001.json, renders/previs/C001.mp4 ... (chỉ nếu file thật)
Chưa đạt: C003 — ... | Đề xuất: sửa cử động tay trong 00:03–00:04
Checkpoint: reports/PRODUCTION_STATUS.json (nếu đã lưu thật)
Chờ: PHÊ DUYỆT SỬA P14/C003 hoặc chấp thuận bước kế tiếp sau khi đủ PASS.
```

Nếu nền tảng hiển thị được nút có callback thật, dùng nút để gửi quyết định; nếu không, dùng câu duyệt rõ trong chat. **Không hứa UI nút chuyên dụng sẵn có trong plugin skills-only.**

## Phục hồi qua phiên và invalidation

- Mở phiên mới: xác minh đúng hostname/deviceId/workspace P00–P02 theo cổng môi trường, đọc `PRODUCTION_STATUS.json` và các manifests/log/sha. Không suy luận vì file tên `FINAL_MASTER.mp4` tồn tại là đã PASS.
- Nếu source CSV/MD thay đổi: so hash; invalidation các công đoạn dùng dữ liệu đó, không xóa hay viết đè nguồn. Nếu dialogue thay đổi: tối thiểu P09/P12/P13 và các cảnh/sequence phụ thuộc cần kiểm lại; nếu asset đổi: chỉ invalidation shot liên quan + P16–P21. Chỉ chọn lại phạm vi sau impact analysis có duyệt.
- Work unit PASS và hash còn hiệu lực → giữ; work unit FAIL/BLOCKED/PENDING → xử lý tiếp theo điều kiện; không rerun toàn bộ phim khi lỗi một shot.
- Phê duyệt cũ không tự động áp dụng khi source, model, codec, dự án hoặc phạm vi tác động thay đổi.

## Bản sửa OpenFilm v1.8.0 — ưu tiên so với ma trận tổng quát

- **P06.08–.11:** verified runtime profile → tạo fixture 7s tự chứa HTML + WAV tone + VTT → render OpenFilm có approval → FFprobe và xem/nghe. Thiếu CLI thì GUI chỉ được chọn nếu đã kiểm chứng. Chưa render thật → `BLOCKED/NOT_TESTED`.
- **P08.05:** chọn nguồn TTS, tạo `VOICE_SOURCE_LOCK.json` chỉ trong dự án được duyệt. VieNeu GPU-first mặc định cho thoại tiếng Việt, CPU theo T07, các provider OpenFilm bị khóa.
- **P09.06:** FilmData validation → tạo `film.html` sớm cùng placeholder scenes (sau duyệt tạo file). Mọi placeholders chưa là asset/cảnh PASS.
- **P10.06–.07:** cân nhắc Canvas; `FILE_STORYBOARD` mặc định và luôn chấp nhận được; chỉ `OPENFILM_CANVAS` nếu verified và phê duyệt, không tạo node TTS gây phí.
- **P14.06:** thay page cảnh placeholder bằng cảnh đã duyệt, không đè Studio overrides hoặc locked tracks.
- **P16.06:** xác minh film.html hợp lệ + placeholder scenes=0 + preview OpenFilm có bằng chứng, trước P17.
- **P17.07:** mở project film.html hiện hữu và hoàn thiện WAV/VTT/SFX/color/cuts; không reset edits, hash dự án và backup.

Nội dung trên ràng buộc thêm chứ không thay quy trình P00–P05; QC riêng từng packet được giữ nội bộ trong macro, không đòi user nghiệm thu từng packet. P18 smoke của phim chính vẫn bắt buộc. Nếu xung đột thứ tự trong các skill cũ, áp dụng bảng này.

## CLI-first override v1.9.0

Với mọi công việc OpenFilm, `A02 CLI` là runtime bắt buộc. P06 ghi CLI profile mode=cli, cwd/evidence; P09 bootstrap `film.html`; P10 `canvas` nếu được duyệt; P14–P16 kiểm hình qua `openfilm look`; P17 timeline code rồi `look`; P18/P19/P21 OpenFilm Master render qua `openfilm render --out` khi help cho phép, Remotion Master OpenFilm CLI render/kiểm previs, Remotion CLI làm master final. Không dùng Desktop UI-only, không gọi npx tải ngầm. Các gói CLI record P06.12/P16.07/P18.05/P21.06 có output thực & checkpoint, nhiều packet trong macro đã duyệt có thể chạy cùng lượt High; chỉ xin duyệt đặc biệt/nhóm, không duyệt mỗi packet.

## v1.10.0 — phê duyệt theo lô, không theo từng packet

Các packet P06.12/P16.07/P18.05/P21.06 được tự QC/log khi nằm trong bundle đã được duyệt; không tạo nút cho metadata/probe trong cùng scope. Riêng download/cài, network first-run, voice provider, GPU→CPU, chi phí, xóa, xuất bản luôn là special action xin duyệt riêng. Sơ đồ batch và action mới xem `openfilm-batch-approval/SKILL.md`.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate

**Cổng thị giác v1.12.0:** M2 (P10/P11) yêu cầu trực tiếp nhận và xem ảnh storyboard/nhân vật/assets; M4 (P14/P15/P16) xem OpenFilm CLI look của từng cảnh; M5 (P17/P18), M6 (P19/P20), M7 (P21) trích hình **từ chính MP4 smoke/draft/master thật** rồi ChatGPT nhìn nhận xét. Chỉ FFprobe/CLI log/JSON hay ảnh tồn tại trên máy không đủ. Nghiệm thu macro bị `validate_macro_event.py` từ chối nếu thiếu Visual QC file/source/image hashes và target/frame coverage. Không thêm phê duyệt cho từng ảnh; sửa/nhìn lại trong phạm vi macro đã duyệt. Nếu connector không đưa ảnh multimodal vào ngữ cảnh ChatGPT, xuất PNG user upload, ghi BLOCKED. Tất cả nghe tiếng và QC20#18 xem liên tục video vẫn riêng; không tuyên bố đã xem cả phim khi chỉ lấy frame mẫu.
