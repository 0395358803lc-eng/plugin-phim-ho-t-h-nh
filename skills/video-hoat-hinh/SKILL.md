---
name: video-hoat-hinh
description: "Điều phối phim hoạt hình code-only theo storyboard JSON/Markdown/FilmData; chọn OpenFilm CLI hoặc Remotion; VieNeu GPU, V01 trước rồi user đánh giá."
---

# Video-hoạt-hình v1.14.3 — Data Storyboard + Dual Engine + Finish First

Đây là plugin kỹ năng điều phối, không mang theo runtime/model/connector máy. Luôn báo dựa trên file thực. Mặc định `FINISH_FIRST_USER_REVIEW`: sản xuất V01, giao người dùng xem, chỉnh V02/V03 theo phản hồi. Giữ 8 macro M0–M7, 99 template packet ID và checkpoint; không hỏi duyệt từng packet hoặc xét QC thẩm mỹ trước khi có video. QC20/visual/audio listen chỉ khi user yêu cầu; kiểm kỹ thuật file cần đủ để không bàn giao video hỏng.

## Hai đường sản xuất được chọn ngang hàng

**P08 phải hỏi/chốt `masterEngine` = `openfilm` hoặc `remotion`**, trừ khi người dùng đã chọn. Không ngầm ép `openfilm` vì dự án mới; dự án cũ đã chốt engine thì giữ. Khi thiếu engine, trình đúng hai lựa chọn, kèm dependencies và sự khác biệt. Không tự chuyển từ engine đã chọn khi gặp lỗi. Ghi `masterEngine` và runtime capability vào `reports/PRODUCTION_PROFILE.json` và FilmData.

- **A — OpenFilm CLI:** CLI được xác minh mới là executor cho các tác vụ OpenFilm; HTML/SVG/Canvas/GSAP/Three.js, `film.html` + scenes, timeline OpenFilm, `openfilm render` ra V01.
- **B — Remotion:** độc lập, code React/TSX với `useCurrentFrame()`/Composition, có thể dùng GSAP hoặc R3F/Three.js; Remotion CLI/renderer kết xuất V01. **Không yêu cầu OpenFilm CLI**, `film.html`, OpenFilm Canvas, `look`, OpenFilm previs hay OpenFilm smoke. Chỉ dùng OpenFilm như công cụ tùy chọn nếu người dùng yêu cầu bổ sung.

**Chính sách engine:** `CLI_ONLY_FOR_OPENFILM` chỉ có nghĩa mọi lệnh OpenFilm phải qua CLI, không phải mọi phim phải dùng OpenFilm CLI. Các hướng dẫn v1.14.1 hoặc cũ yêu cầu `CLI_REQUIRED` với Remotion, dựng OpenFilm skeleton bắt buộc hoặc OpenFilm previsualization bắt buộc đã được thay thế bởi nhánh engine cụ thể trong v1.14.3. Không tự cài Node/Remotion, Chromium, OpenFilm hay model: rà reuse trong workspace cũ; danh mục thiếu và thao tác đặc biệt cần phê duyệt riêng.

## Storyboard P10 = DỮ LIỆU, KHÔNG PHẢI ẢNH

Đọc **[openfilm-storyboard-data](../openfilm-storyboard-data/SKILL.md)** làm hợp đồng áp dụng trước các kỹ năng upstream. P10 bắt buộc tạo `storyboard/storyboard.json`, `storyboard/STORYBOARD.md` liên kết từng shot FilmData, mô tả bố cục/hành động/camera/thời gian/chuyển động/nhân vật/ánh sáng. Character/style bible chỉ là thông số định lượng và mô tả. Không gọi image generator để làm storyboard, không node picture/portrait/fullBody/turnaround16, không tạm render ảnh, không rasterize, không Canvas Make/Make all. `FILE_DATA_STORYBOARD` là mặc định cố định. P10 `OUTPUT_READY` dựa dữ liệu parse được và mapping đúng; không chờ ảnh/visual inspection.

P11 chỉ chuẩn bị asset thực sự xuất hiện trong cảnh: **ưu tiên code SVG, CSS, Canvas, TSX, geometry/mesh/shader/Three.js, không sinh ảnh**. Nếu shot code-only: ghi `imageAssets=[]`, không ZIP handoff, không yêu cầu PNG. Media ảnh sẵn có do người dùng cấp chỉ là tùy chọn theo yêu cầu cụ thể, phân biệt rõ với storyboard. `openfilm-image-zip-handoff` không nằm trên đường phụ thuộc mặc định.

## Quy trình điều phối

M0 P00–P06: xác minh máy được chọn, root `VIDEO_HOAT_HINH_WORKSPACE`, reuse và kiểm tra **runtime engine đã chọn**, phê duyệt cài khi cần; không rà/cài engine không dùng. M1 P07–P09: đọc đủ 7 file nguồn, chốt A/B, tạo FilmData integer frames; bootstrap `film.html` **chỉ nhánh A**, tạo Remotion project/Composition skeleton **chỉ nhánh B**. M2 P10–P11: storyboard data + assets code-only. M3 P12–P13: VieNeu GPU WAV khi có thoại, phụ đề theo thời lượng thật. M4 P14–P16: scene code theo master, `.html` cho A hoặc `.tsx` cho B, không để placeholder thật cản render. M5 P17–P18: một timeline master theo engine; P18 smoke chỉ chẩn đoán/theo yêu cầu. M6 P19–P20: render V01 theo engine, kiểm MP4, P20 chỉ sau phản hồi. M7 P21: bàn giao video, mã nguồn, WAV, phụ đề, manifest, rồi user quyết định chấp nhận/chỉnh.

Bỏ packet riêng engine không được chọn bằng `SKIPPED_ENGINE_NOT_SELECTED` với skipReason và evidencePaths (đường dẫn báo cáo master/stage thật); không đặt file giả hoặc đánh dấu PASS khống. Packet code-only vẫn phải tạo file thật, kiểm hash/parse. `OUTPUT_READY` nghĩa đầu ra tồn tại và dùng được, `DELIVERED_FOR_REVIEW` video đã giao, `USER_ACCEPTED` chỉ khi người dùng xác nhận. Không chạy nền và không tự publish.

## Danh mục kỹ năng

`openfilm-moi-truong` cho máy/workspace và reuse có điều kiện; `openfilm-hybrid-master` chọn engine; `openfilm-filmdata` FilmData; `openfilm-kich-ban` brief/beat; **`openfilm-storyboard-data` P10/P11** (ưu tiên hơn `openfilm-canvas` legacy); `openfilm-animation`, `openfilm-gsap`, `openfilm-threejs` cảnh A; `openfilm-remotion`, `openfilm-remotion-r3f` cảnh B; `openfilm-vieneu-tts` WAV; `openfilm-audio-subtitles` subtitles; `openfilm-timeline` timeline; `openfilm-production-p06-p21`, `openfilm-macro-bundles`, `openfilm-high-workpackets` triển khai và checkpoints; `openfilm-render-profiles` render; `openfilm-checkpoint-approval` bàn giao và phiên bản. Chỉ dùng `openfilm-cli-execution` cho lệnh OpenFilm thật; không áp lên Remotion. `openfilm-image-zip-handoff`, `openfilm-visual-inspection`, `openfilm-qc-advanced` theo yêu cầu cụ thể, không phải dependency.

Quyền PACKAGE_INSTALL, MODEL_DOWNLOAD, BROWSER_DOWNLOAD, SYSTEM_CHANGE, GPU_TO_CPU_FALLBACK, VOICE_CLONING, EXTERNAL_PROVIDER, PAID_ACTION, DELETE, PUBLISH, OUT_OF_SCOPE vẫn tách riêng. Một scope production được duyệt có thể bao phủ M1–M7; thay đổi scope/input/engine cần đánh giá lại quyền. Mọi lệnh, hashes, checkpoint có bằng chứng; giữ nguyên các phiên bản cũ và chỉ ghi nhận user acceptance từ user.
