# Video-hoạt-hình v1.11.0 — 8 macro-bundle M0–M7

**Mặc định cho dự án mới:** gộp công việc xuyên P00–P21 theo M0 (P00–P06), M1 (P07–P09), M2 (P10–P11), M3 (P12–P13), M4 (P14–P16), M5 (P17–P18), M6 (P19–P20) và M7 (P21). 99 mẫu packet giữ nguyên để QC/checkpoint **nội bộ**, không sinh phê duyệt từng packet/Pxx. Những P00–P05 cần người dùng chọn máy/path và cài/tải/first-run render có phê duyệt riêng. Mỗi macro có một approval scope được trình minh bạch, một turn High có thể xử lý nhiều packet; khi kết thúc lượt, nút `Tiếp tục nhóm đã duyệt` gửi turn mới không cần phê duyệt lại. Plugin không chạy ngầm.

Nguồn điều phối: `skills/openfilm-macro-bundles/SKILL.md`, `references/MACRO_POLICY.json`, `macro_scheduler.py`, `validate_macro_event.py`. Skill `openfilm-batch-approval` dùng **LEGACY** cho history v1.10, không phải đường mặc định. Bốn thứ tự template P06.12/P10.06/P14.06/P17.07 đã sửa trước các cổng render/QC/khóa. Stage QC nội bộ không tự nhận là user acceptance. OpenFilm CLI-first và VieNeu-TTS CUDA GPU-first không thay đổi; cài/tải model/Chromium, CPU fallback, voice cloning, khoản phí/xuất bản/xóa/ngoài phạm vi cần duyệt riêng. Toàn bộ QC video phải dùng file thật.

---

## Tài liệu kỹ thuật lịch sử v1.3–v1.10 (không ghi đè cơ chế v1.11)

# Video-hoạt-hình · v1.7.0 Hybrid Pipeline + High packets + GPU-first VieNeu-TTS

Plugin skills-only tiếng Việt giữ 14 kỹ năng v1.3.0 và thêm 7 kỹ năng chuyên sâu theo **báo cáo deep-research-report (1).md** (19/11/2026). Tổng **26 skills**. Bộ plugin **không** cài OpenFilm/Remotion/VieNeu, không kèm model hoặc app server MCP.

## Quy trình khi dùng Windows

P00 chọn và xác minh máy → P01 hỏi thư mục dự án → P02 tạo/xác nhận `<PROJECT_DIR>\VIDEO_HOAT_HINH_WORKSPACE` → P03 tìm workspace cũ trong phạm vi được cấp quyền → P04 kiểm kê OpenFilm, Node/FFmpeg/Chromium, GSAP/Three/Remotion/VieNeu, các mục B05–B10 có điều kiện → P05 liệt kê thiếu để **chờ phê duyệt**. Không tự cài, không sửa driver/OS, không đổi PATH/copy workspace.

Sau khi được duyệt làm production: **OpenFilm Master** mặc định (tự xuất MP4) hoặc **Remotion Master** (OpenFilm tạo previs/assets; Remotion timeline+render cuối). Handoff bằng file, không có API chuyển JSX/film.html trực tiếp. Có một dữ liệu FilmData frame chuẩn, asset manifest, phụ đề/nhạc/voice theo master duy nhất, QC20 và smoke 5 giây.

## Các kỹ năng mới

- `openfilm-hybrid-master`: N01–N02
- `openfilm-filmdata`: N03–N05 (bao gồm validator Python stdlib)
- `openfilm-sample-90s`: N06 (fixture 6 shot/7 dialogue, chưa render)
- `openfilm-remotion-r3f`: N07/N09
- `openfilm-audio-subtitles`: N10–N12
- `openfilm-render-profiles`: N13/N15/N17
- `openfilm-qc-advanced`: N14/N16/N18

N08 GSAP–Remotion được tích hợp trong kỹ năng `openfilm-gsap` và `openfilm-remotion`; xem `N01-N18-COVERAGE.md` để tra đầy đủ. Source chỉ cung cấp hướng dẫn và ví dụ; muốn kiểm tra render phải kết nối máy Windows thật, phê duyệt cài/dựng và có media thực.

Kiểm fixture: `python skills/openfilm-filmdata/references/validate_filmdata.py skills/openfilm-sample-90s/references/film.json`. Kiểm actual WAV dùng thêm `--check-assets <project-root>`; fixture gốc sẽ báo thiếu WAV **đúng dự kiến**.

## Quy trình P06–P21 sau khi có 7 tệp kịch bản (v1.5.0)

Giữ nguyên P00–P05. Sau P05 phải duyệt cài đặt (nếu thiếu) và duyệt phạm vi sản xuất riêng. `openfilm-production-p06-p21` định nghĩa 16 phase P06–P21; `openfilm-script-input` kiểm kê 7 tệp đầu vào; `openfilm-checkpoint-approval` giữ checkpoint/QC/approval theo từng cảnh/thoại/asset qua nhiều phiên. Không tự viết lại 7 tệp nguồn và không giả kết quả render.

- Ma trận đầy đủ: `skills/openfilm-production-p06-p21/references/P06-P21-WORKFLOW.md` và `STAGE_DEFINITIONS.json`.
- Template checkpoint: `skills/openfilm-checkpoint-approval/references/PRODUCTION_STATUS_TEMPLATE.json`, validator stdlib Python.
- Script kiểm kê nguồn read-only: `skills/openfilm-script-input/references/audit_seven_files.py`.
- Môi trường, render và chất lượng giọng thật vẫn chỉ được nghiệm thu sau khi chạy trên máy Windows được cấp quyền.

## High work packets và duyệt một chạm (v1.6.0)

Giữ nguyên P00–P05 và 7 tệp kịch bản. **Toàn bộ 16 stage P06–P21** được phân rã trong `skills/openfilm-high-workpackets/references/WORKPACKET_DEFINITIONS.json` thành template mở rộng động theo shot/asset/dialogue/issue. Mỗi lượt xử lý **một work packet**, checkpoint sau công việc và trả bảng QC.

`skills/openfilm-oneclick-approval/SKILL.md` mô tả các nút `Phê duyệt thực hiện`, `Nghiệm thu & làm tiếp`, `Phê duyệt sửa`, `Xem chi tiết`, `Tạm dừng`: khi **host hỗ trợ UI** callback, bấm nút gửi `GenUI.issueNewTurn` với câu phê duyệt có scope, không cần tự gõ. Sau khi click, với workflow mới v1.11, ChatGPT đọc lại checkpoint và có thể chạy nhiều packet thuộc macro đã duyệt; chỉ workflow LEGACY v1.6 áp dụng một packet. Không chạy trong nền. Không hỗ trợ UI thì dùng tin nhắn ngắn; skill-only không thể bảo đảm nút được render trên mọi thiết bị. Không thể buộc model vào High, người dùng chọn trong model/effort settings.

File `WORK_UNIT_INDEX.json` là nguồn thứ tự/resume; `PRODUCTION_STATUS.json` bản v1.5 giữ nguyên schema 1. Validator stdlib chỉ đọc: `skills/openfilm-high-workpackets/references/validate_work_packets.py`. Các đường dẫn output/asset trong template là kế hoạch; không có bằng chứng thực trên Windows cho đến khi chạy.

## VieNeu-TTS GPU-first (v1.7.0)

Nếu bật VieNeu-TTS, P04/P05 ưu tiên NVIDIA GPU + PyTorch CUDA, kiểm GPU/VRAM/driver và bản wheel Windows, tái sử dụng GPU venv/model cũ trước. P06 có gate CUDA runtime + tạo WAV smoke thật sau phê duyệt; P12 không được âm thầm dùng CPU. Khi GPU không đáp ứng sau kiểm tra/sửa trong phạm vi cho phép, lập báo cáo nguyên nhân và trình CPU/ONNX T07 để user phê duyệt riêng. Chi tiết `skills/openfilm-vieneu-tts/references/GPU_FIRST_POLICY.md` và `skills/openfilm-moi-truong/references/VIENEU-TTS-WINDOWS.md`. Không sửa driver/CUDA/toolkit hay cài ngoài workspace.

## v1.8.0 — Sửa 5 điểm OpenFilm

(1) `P06.08` kiểm capability Desktop/CLI thực qua `OPENFILM_RUNTIME_PROFILE.json`. (2) `P09.06` tạo `film.html` + placeholder scenes ngay sau FilmData, `P16.06` từ chối placeholder. (3) `P10.06–.07` chọn Canvas chỉ khi đã kiểm chứng, mặc định file storyboard. (4) `P08.05/P12.08` khóa VieNeu GPU-first, không cho OpenFilm Canvas/get gọi giọng ngoài. (5) `P06.09–.11` fixture OpenFilm E2E 7 giây (ảnh động, WAV tone 48kHz, VTT, FFprobe + xem/nghe thật) trước phim dài; P18 smoke master vẫn độc lập. Phân gói High giữ nguyên ở tầng kỹ thuật nhưng nút phê duyệt theo macro v1.11, không theo từng packet. Chưa cài/render máy nào khi sửa plugin.

## v1.9.0 — OpenFilm CLI là runtime chính

Plugin không sử dụng OpenFilm Desktop UI để thực thi thay CLI. `openfilm-cli-execution` quy định A02 CLI bắt buộc, Node>=22.2, FFmpeg/FFprobe, Chromium compatible, dùng lại bản cài cũ hợp lệ trước khi đề nghị download/install. P06 ghi OpenFilm CLI profile mode=cli và có E2E 7s từ CLI thật. P09 bootstrap `film.html`, P14–P16 `look`, P18/P19/P21 nếu OpenFilm Master dùng `render` từ CLI ở cwd project; Remotion Master dùng CLI OpenFilm cho previs, Remotion CLI cho final. Studio chỉ là viewer tùy chọn qua `openfilm open` sau duyệt. Không tự `npx @latest`, không cài global, không download browser chưa duyệt. One-click approval/checkpoint/GPU VieNeu giữ nguyên.

## v1.10.0 — Reduced-Click Approval Bundles

99 work packet templates remain internal QC/checkpoint primitives, **not 99 user approvals**. Group tasks into visible, bounded bundles (typically 1–3 per stage for ordinary projects) according to `skills/openfilm-batch-approval/references/BUNDLE_POLICY.json`. One approval may execute multiple compatible packets in a High turn, with QC/checkpoints at every step. When a bundle cannot finish in one turn, offer **Tiếp tục lô đã duyệt** without requesting a fresh approval; user must still click to start a new turn. Show buttons for bundle plan, bundle acceptance, repair, or extraordinary risks only. No background execution, no unapproved installs/downloads/provider changes/CPU fallback.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate
### v1.12.0 — Mandatory Visual Inspection & Quality Gate

M2/M4/M5/M6/M7 cần ChatGPT nhận và quan sát ảnh thật, không chỉ đọc metadata. Dùng Remote Desktop Commander `read_file`/`read_multiple_files` hoặc ảnh do user upload. M2 nhìn storyboard/nhân vật/bối cảnh, M4 nhìn OpenFilm CLI look theo shot, M5/M6/M7 nhìn frame trích từ các MP4 smoke/draft/master thực; JSON receipt + file/SHA256 + sample coverage được `openfilm-visual-inspection` kiểm. Kết quả thị giác cần mô tả riêng theo cảnh và không được tự tuyên bố xem trọn video từ vài frame. Không truyền ảnh được → `VISUAL_BLOCKED`. Giữ 8 macro, 99 packet, OpenFilm CLI và GPU VieNeu; không tăng lượt bấm cho từng ảnh.
