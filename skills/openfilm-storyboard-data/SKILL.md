---
name: openfilm-storyboard-data
description: "P10 storyboard DATA_ONLY bằng JSON/Markdown/FilmData cho cả OpenFilm CLI hoặc Remotion, hoàn toàn không tạo ảnh storyboard."
---

# Storyboard as Data — v1.14.2 (chính sách bắt buộc)

Áp dụng khi tạo phim mới và khi sửa cảnh cũ. Mọi hướng dẫn đời trước về picture nodes, PNG storyboard, rasterize panels, canvas Make/Make all, file ảnh trung gian, ZIP handoff và cổng VISUAL_BLOCKED tại M2 đều không áp dụng cho đường sản xuất mặc định. **Không gọi image generation, không tạo ảnh storyboard, không buộc user nhận ZIP/giải nén**. Chỉ được đưa asset ảnh có sẵn vào cảnh nếu người dùng đã cung cấp/duyệt cụ thể; không bao giờ coi asset ảnh là storyboard. Tạo chuyển động và hình dạng bằng mã HTML/SVG/CSS/Canvas/GSAP/Three.js hoặc TSX/React/Remotion và R3F phù hợp master.

## Hợp đồng dữ liệu P10

- Input: `projects/<film-id>/scene-data/film.json`, bảy tệp nguồn, style/character bibles.
- Output bắt buộc: `projects/<film-id>/storyboard/storyboard.json` và `projects/<film-id>/storyboard/STORYBOARD.md` (file thực, không placeholder). Tùy chọn `storyboard/shots/<shot-id>.md`.
- Mỗi shot: `shotId`, `sceneId`, `startFrame`, `durationInFrames`, `fps`, `layout`, `characters` (vị trí, state, expression), `action` (event theo frame), `camera` (framing, position, move), `background` (code/geometry), `lighting`, `motion` (keyframes/easing), `audioIds`, `subtitleIds`, `transition`, `implementation` (`svg|html|canvas|threejs|tsx|r3f`), `assetRefs` (chỉ file thực), `notes`.
- Tất cả thời gian chuẩn bằng frame nguyên theo FilmData; shotId duy nhất, khớp 1:1 danh sách shot; nhân vật và palette nhất quán. Không sinh pixel để chứng minh storyboard hợp lệ.
- P10 READY khi JSON parse được, mapping/timing/fields hoàn chỉnh và tệp MD hiện hữu. Không phụ thuộc Canvas CLI, ảnh hoặc nhận xét thẩm mỹ.

## P11 assets code-only

- Tạo SVG/HTML/CSS/JS/TSX/mesh/material/geometry bằng code hoặc import font/WAV/media đã được cấp phép. Không sinh/đòi PNG vì storyboard.
- Nếu cảnh không tham chiếu ảnh thì `imageAssets=[]`, `imageGeneration=SKIPPED_NOT_REQUIRED`, `zipHandoff=SKIPPED_NOT_REQUIRED` và tiếp tục P12/P14 bình thường.
- Nếu thật sự cần PNG/texture từ nguồn hợp lệ đã được người dùng cấp, kiểm file và hash như media thực; `openfilm-image-zip-handoff` chỉ áp dụng yêu cầu chuyển PNG cụ thể, không phải giai đoạn bắt buộc.

## Hai master engine chính thức

`masterEngine = openfilm | remotion`, được người dùng chọn tại P08, không tự đổi.

- `openfilm`: xác minh OpenFilm CLI; dựng `film.html` và `scenes/<shotId>.html`, `window.film.frame(t)` (GSAP seek/Three.js state theo t), render bằng OpenFilm CLI.
- `remotion`: xác minh Node/React/Remotion CLI hoặc renderer, Chromium/FFmpeg nếu cần; tạo `remotion/src/scenes/*.tsx` và Composition, render **trực tiếp bằng Remotion**. Không đòi OpenFilm CLI, film.html, OpenFilm canvas/look/render/previs hay fixture OpenFilm nếu không tham gia dự án.
- Khi Remotion được chọn, các packet chỉ phục vụ OpenFilm phải ghi `SKIPPED` với `skipReason=SKIPPED_ENGINE_NOT_SELECTED` và `evidencePaths` trỏ đến báo cáo quyết định engine thực tế (ví dụ `reports/PRODUCTION_PROFILE.json` hoặc báo cáo nhánh), không tạo file giả để qua gate. Các packet chung FilmData/storyboard/WAV/timeline/render/MP4 vẫn thực hiện.
- Khi OpenFilm được chọn, không đòi Remotion packages hay composition nếu không dùng.

## Chính sách ưu tiên

Tệp này + `skills/video-hoat-hinh/SKILL.md` và định nghĩa P06–P21 v1.14.2 ưu tiên trước những văn bản upstream/legacy có câu `CLI_REQUIRED` vô điều kiện, `Canvas picture/Make`, `image ZIP required`, `M2 VISUAL_BLOCKED` hoặc `OpenFilm preview mandatory`. Giữ quyền người dùng riêng cho tải/cài, ngoại mạng, phí, xóa, đổi CPU, xuất bản; giữ Finish First V01.

## Tương thích 99 packet legacy

Một số template cũ vẫn có tên OpenFilm-only hoặc Canvas-only. Không xóa/đổi ID vì checkpoint cũ cần đối chiếu. Với Remotion, các packet OpenFilm-only P09.06 (bootstrap `film.html`), P14.06, P16 preview/CLI look và render event OpenFilm phải `SKIPPED` có `skipReason` và `evidencePaths` trỏ vào bản profile đã chọn; các đầu ra tương đương Remotion ở stage engine hiện tại phải là file thật. Với **cả hai** engine, P10.06 ghi lựa chọn `FILE_DATA_STORYBOARD` và P10.07 Canvas-only **SKIPPED** có lý do/bằng chứng; P10.05 chỉ tổng hợp tính đầy đủ của JSON/Markdown, không thẩm mỹ QC. P11.02 tạo assets bằng code và khai báo outputPaths là tệp thật, không dùng đường dẫn thư mục; P11.03 SKIPPED khi không dùng 3D; `image ZIP` hoàn toàn SKIPPED nếu không có media ảnh được người dùng yêu cầu.

`macro_scheduler.py` đòi cả `skipReason` **và** `evidencePaths` cho packet SKIPPED. Không chỉ ghi SKIPPED bằng lời hay tên thư mục; nếu packet không cần chạy, ghi đúng sự kiện và file bằng chứng.
