---
name: openfilm-production-p06-p21
description: "Điều phối 16 cổng P06–P21 sau khi Video-hoạt-hình hoàn tất P00–P05: nghiệm thu môi trường, ingest 7 tệp kịch bản, storyboard, asset, VieNeu-TTS, 2D/3D, preview, smoke, draft, QC20 và master MP4 có checkpoint."
---

# Video-hoạt-hình: công đoạn sản xuất P06–P21 (v1.11.0)

## Điều kiện vào và thứ tự cổng

1. **Phải hoàn thành P00–P05 trước** theo `video-hoat-hinh` và `openfilm-moi-truong`; kết nối máy, hỏi thư mục người dùng chọn, tạo/xác nhận `VIDEO_HOAT_HINH_WORKSPACE`, tìm workspace cũ, kiểm kê phần mềm, báo thiếu. P05 là cổng báo cáo và **DỪNG**; không coi phê duyệt nâng cấp skill là phê duyệt cài đặt hoặc làm phim trên máy.
2. P06 chỉ được cài các ID **đã được duyệt rõ ràng** ở P05. Nếu không cần cài, ghi `SKIPPED` với bằng chứng xác minh môi trường, không gọi installer. Nếu còn thiếu runtime bắt buộc mà không được duyệt, `BLOCKED`.
3. P07 phát hiện thư mục chứa **7 tệp kịch bản** mà người dùng đã đặt trong workspace. Thư mục có thể có tên khác `du-lieu-kich-ban`; không tự đặt lại tên hoặc xóa nội dung. Không có tệp thật thì `BLOCKED`, không tự dựng kịch bản giả.
4. Mỗi Pxx: **PLAN (đã bao hàm trong macro đã duyệt) → các packet kỹ thuật → QC từng packet và Pxx → đi tiếp Pxx thuộc cùng macro khi đủ QC; chỉ xin user nghiệm thu tại ranh giới macro**, trừ cổng quyền đặc biệt/quyết định hình/âm. P07 đọc/kiểm tra trước có thể chạy read-only trong phạm vi đã cho; sửa dữ liệu nguồn vẫn phải xin duyệt riêng và ưu tiên tạo bản sửa tại thư mục project.
5. Checkpoint theo `openfilm-checkpoint-approval`; lưu `reports/PRODUCTION_STATUS.json`, đơn vị theo shot/thoại, đầu ra hash/paths/log/QC, approval, scope đã duyệt. Lần gọi tiếp theo: đọc checkpoint + file thật, xác minh hiệu lực bằng hash trước, chỉ chạy unit chưa đạt hoặc bị invalidated, không lặp công việc PASS hợp lệ.
6. Đọc `references/P06-P21-WORKFLOW.md` và `references/STAGE_DEFINITIONS.json`; dùng `openfilm-script-input` cho P07, `openfilm-filmdata` cho P09, `openfilm-hybrid-master` cho P08/P17, `openfilm-qc-advanced` cho P18/P20/P21.

## Ma trận 16 cổng công việc

| Cổng | Mục tiêu / đầu ra kiểm chứng | Kỹ năng liên quan |
|---|---|---|
| P06 | Cài đúng ID đã duyệt và nghiệm thu môi trường; VieNeu-TTS ưu tiên GPU CUDA, TTS GPU smoke PASS hoặc CPU fallback được duyệt; nếu không dùng TTS thì SKIPPED có lý do | `openfilm-moi-truong` |
| P07 | Đọc đúng 7 tệp, kiểm chứng CSV/markdown, lập `INPUT_AUDIT.md` | `openfilm-script-input` |
| P08 | Chốt style/profile và `openfilm|remotion` master, phê duyệt rõ | `openfilm-hybrid-master`, `openfilm-render-profiles` |
| P09 | Chuẩn hoá `film.json`, `shots.json`, `dialogues.json`, asset manifest | `openfilm-filmdata` |
| P10 | Style bible, character bible, storyboard từng cảnh được duyệt | `openfilm-kich-ban`, `openfilm-canvas` |
| P11 | Dựng/kiểm asset hình, model, font, provenance, không bịa file | `openfilm-media`, `openfilm-threejs` |
| P12 | VieNeu-TTS WAV từng câu **GPU CUDA/PyTorch là ưu tiên**, kiểm gate backend; chỉ CPU/ONNX nếu được duyệt riêng; nghe và FFprobe | `openfilm-vieneu-tts` |
| P13 | Đồng bộ thời gian WAV thật và subtitles SRT/VTT, chỉ có timestamp có căn cứ | `openfilm-audio-subtitles`, `openfilm-filmdata` |
| P14 | Dựng/chứng minh chuyển động 2D từng shot bằng GSAP/HTML hoặc React | `openfilm-gsap`, `openfilm-animation` |
| P15 | 3D bằng Three.js/R3F/WebGL, chỉ nếu shot cần, có thể SKIPPED | `openfilm-threejs`, `openfilm-remotion-r3f` |
| P16 | OpenFilm previs/preview từng cảnh và nghiệm thu camera/hình/chuyển động | `openfilm-qc-render`, `openfilm-canvas` |
| P17 | Lắp ráp master timeline, audio/ducking, captions, color đúng engine | `openfilm-hybrid-master`, `openfilm-timeline`, `openfilm-color` |
| P18 | Smoke video 5 giây có hình, tiếng khi được yêu cầu; ffprobe & xem/nghe | `openfilm-qc-advanced` |
| P19 | Render draft toàn phim, kiểm tra metadata/duration/shot boundaries | `openfilm-render-profiles` |
| P20 | QC20 toàn phim, báo lỗi theo scene, fix chọn lọc + re-QC | `openfilm-qc-advanced` |
| P21 | Render master, FFprobe, phát kiểm, xuất `FINAL_MASTER.mp4` + phụ đề/source/báo cáo | `openfilm-qc-render` |

## Khác biệt giữa hai master

- **OpenFilm Master (mặc định)**: shot là trang HTML, `window.film.frame(t)` deterministic, audio track trong `film.html`, OpenFilm render master. Remotion là công cụ render clip riêng nếu có duyệt.
- **Remotion Master**: OpenFilm để previs/chỉnh shot; `FilmData` làm contract, React/GSAP/R3F/Remotion xử lý timeline, audio, captions và master; giao tiếp OpenFilm ↔ Remotion qua file/asset/previs có thật, không có API chuyển nguyên vẹn HTML→JSX.
- Master được chốt tại P08; nếu đổi về sau, trình impact analysis (dependency, license, re-render, trạng thái những Pxx có ảnh hưởng) và xin duyệt, không tự đổi.

## Công việc kỹ thuật vẫn chia để kiểm chứng, nhưng không bắt duyệt lẻ

P11 theo asset_id, P12 dialogue_id, P14/P15/P16 shot_id, P17 sequence, P20 issue. `openfilm-macro-bundles/SKILL.md` gộp nhiều Pxx trong một macro đã được duyệt; kết thúc mỗi packet chỉ ghi QC/checkpoint nội bộ. Không cần click sau từng packet hoặc Pxx nội bộ. Chỉ khi hết lượt High, blocker, cổng người dùng hoặc xong macro mới hiển thị một nút chính.

## Điều kiện dừng

- Người dùng chưa duyệt giai đoạn hoặc sửa: `WAITING_APPROVAL`/`BLOCKED`; nếu không có nút phê duyệt thật, đưa câu xác nhận theo ID trong chat. Không tạo nút giả.
- Thiếu/khác dữ liệu 7 tệp: dừng P07; không tự điền nhân vật, lời thoại, shot chưa có.
- TTS chưa có WAV/không nghe được: P12/P13 chưa PASS. Nếu remote không chuyển âm thanh, đưa đường dẫn/file mẫu có thật để user tải/gửi lên chat; không giả nói đã nghe.
- P18 hoặc P20 FAIL thì dừng trước master, báo hạng mục lỗi + phương án sửa + xin duyệt; chỉ chạy lại phần bị ảnh hưởng.
- Chỉ P21 PASS khi master MP4 tồn tại và **kiểm tra phát được**; không biến việc tạo JSON, render log hay ffprobe đơn lẻ thành bằng chứng đã hoàn thành phim.

Plugin là kỹ năng điều phối, không nhúng runtime/engine, không tự thực thi Windows nếu không có kết nối/ủy quyền.

## Phân công High v1.11.0 — ưu tiên macro

99 packet là checklist; sử dụng `openfilm-macro-bundles/references/macro_scheduler.py` để lên thứ tự đúng, stage QC và special boundaries. **LEGACY:** mọi câu cũ kiểu "một packet một lượt/một nút" chỉ áp dụng checkpoint cũ, không áp dụng dự án mới. Khi không thể chạy hết nhóm trong lượt High thì tiếp tục cùng macro sau một nút, không đòi lại phê duyệt.

## Chính sách GPU TTS v1.7.0

P06 cần phân gói preflight GPU read-only T06, cài T05 trong venv chỉ sau duyệt, test torch CUDA và WAV smoke GPU đã được duyệt, lưu `reports/tts/GPU_DECISION.json`; khi GPU không đáp ứng chỉ trình đề xuất ONNX T07 kèm nguyên nhân/evidence và approval ID CPU riêng. P12 phải kiểm lại backend khi chạy từng batch, từ chối silent fallback sang ONNX. Không đánh dấu `P06 PASS` vì package CUDA hiện diện; cần thực chạy GPU kiểm chứng hoặc gói `CPU_FALLBACK_APPROVED` có chứng cứ. Chỉ hỏi duyệt CPU fallback riêng; packet TTS kiểm chứng GPU thông thường kế thừa macro M0/M3 v1.11.0, không phát nút riêng sau từng packet.

## Trình tự sửa OpenFilm v1.8.0

P06: Sau cài/reuse kiểm kê capability Desktop/CLI và ghi `OPENFILM_RUNTIME_PROFILE.json` (P06.08); trước smoke có thể đánh dấu renderClip=UNVERIFIED, đây là phép thử đầu tiên, tạo E2E fixture 7s có WAV+VTT được duyệt (P06.09), chạy OpenFilm render thật (P06.10), FFprobe và xem/nghe xác nhận (P06.11), rồi mới chốt P06.04. Nếu OpenFilm CLI không tồn tại nhưng Desktop GUI verified thì thực hiện trong GUI sau duyệt; không có renderer được điều khiển → BLOCKED, không PASS ảo. P08.05: khóa nguồn `vieneu-local` nếu dùng lời thoại. P09.06: bootstrap `film.html` + scene placeholders từ FilmData đã validate; chưa QC hình. P10.06–P10.07: Canvas optional, default FILE_STORYBOARD; Canvas làm board không tạo TTS/provider. P12.08: xác minh source-lock + backend GPU-first trước WAV. P14.06: thay placeholder bằng scene đã hoàn thiện, giữ edits. P16.06: kiểm placeholder=0 và preview scene từ runtime verified; P17.07: hoàn thiện file timeline đã tạo từ P09, không dựng mới từ đầu. Chia từng công việc High và nút phê duyệt/kiểm tra theo `openfilm-oneclick-approval`. Bản cập nhật plugin chỉ là **hướng dẫn/mã kiểm tra**, chưa phải lần chạy thực trên Windows.

## Đường thực thi OpenFilm CLI-first v1.9.0

Bất kỳ Pxx dùng OpenFilm bắt buộc đọc `openfilm-cli-execution/SKILL.md` và profile mode `cli`, xác minh CLI A02 từ P04/P05/P06 trước. P09 tạo film.html sớm offline, P14–P16 check bằng `look`, P17 hoàn thiện timeline, P18/P19/P21 nếu OpenFilm Master render bằng CLI; Remotion Master OpenFilm CLI chỉ làm previs/ảnh QC và Remotion CLI final. P06 CLI 7 giây có log stdout/stderr, exitCode và MP4 thật; không dùng Desktop UI-only, không tự tải qua npx. Mỗi CLI run là một work packet có approval, cwd cố định trong workspace và chứng cứ.

## v1.11.0 — 8 macro-bundle M0–M7

P00–P05 cổng chuẩn bị; P06 trong M0. M1 P07–09, M2 P10–11, M3 P12–13, M4 P14–16, M5 P17–18, M6 P19–20, M7 P21. **Không duyệt từng packet hay từng stage**. Điểm P08 profile, P10 visual, P12 voice, P13 listening (nếu có thoại), render đầu tiên, cài/tải/CPU fallback và final acceptance vẫn có phê duyệt riêng. Đọc `openfilm-macro-bundles/SKILL.md` + OPERATIONS trước khi thực thi.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate
Ràng buộc P10/P11 (`M2`), P14/P15/P16 (`M4`), P17/P18 (`M5`), P19/P20 (`M6`), P21 (`M7`): `VISUAL_PASS` từ hình ảnh **nhận trong ngữ cảnh thị giác của ChatGPT** là điều kiện nghiệm thu macro độc lập với technical QC. Dùng OpenFilm CLI `look` cho scene (M4), FFmpeg trích chính MP4 đã render cho smoke/draft/master; thiếu image delivery thì `VISUAL_BLOCKED`. Chi tiết `openfilm-visual-inspection/SKILL.md`. Bất kỳ hướng dẫn cũ nói chỉ xem ảnh có trong workspace, hoặc cho PASS từ FFprobe/log, đều không còn đủ.
