# Production Playbook v1.14.2 — code-only + two engines

## 0. Quyền và sản phẩm

Trong scope đã duyệt thực hiện đủ V01 trước bàn giao, không xét QC từng take/frame/packet. Kiểm file thật, hash, decode, audio stream và profile; người dùng quyết định thẩm mỹ sau V01. Không tự cài/tải/phát hành/đổi GPU→CPU khi thiếu quyền.

## M0–M1: môi trường và FilmData

Chọn máy/workspace, reuse tools; chốt `masterEngine=openfilm|remotion` ở P08. A chỉ bắt CLI OpenFilm, B chỉ bắt runtime Remotion/React/Node/renderer và các dependency của nó. FilmData `film.json` có filmId, masterEngine, fps, width, height, durationInFrames, shots (`id`, startFrame, durationInFrames), dialogues (`shotId`, text, startFrame, endFrame), asset references; integer frames và IDs nhất quán. Giữ bảy nguồn không sửa.

A bootstrap `openfilm/film.html` và `openfilm/scenes/*.html`. B bootstrap `remotion/src/Root.tsx`/Composition và cảnh TSX; **không bắt film.html**. Input thay đổi phải kiểm approval scope mới.

## M2: Storyboard như dữ liệu

`storyboard/storyboard.json` và `storyboard/STORYBOARD.md` bắt buộc; shot data có ID, scene, frame start/duration, layout, nhân vật/vị trí/trạng thái, action, camera path, background, lighting, transition, motion keyframes, audio/subtitle refs, implementation và assetRefs. `style-bible.md` + `characters/*.md` là dữ liệu. Map shot IDs và frame đúng FilmData. Không sinh ảnh tĩnh, no thumbnails/portrait/panels/Canvas picture/ZIP; schema xem `openfilm-storyboard-data/references/STORYBOARD_SCHEMA.json`. Kiểm P10 bằng parse, completeness và consistency, không bằng pixel.

P11 lập `assets-manifest.json`: liệt kê SVG/HTML/CSS/TSX/shader/Three.js mesh/texture code và media hiện hữu. Nếu code sinh được scene mà không cần file ảnh thì `imageAssets=[]`, `zipHandoff=SKIPPED_NOT_REQUIRED`. Không giả định asset phải là PNG, không tạo ZIP ảnh để giao người dùng. Chỉ asset thiếu *và thực sự được scene tham chiếu* mới là lỗi blocking.

## M3: WAV + phụ đề

VieNeu-TTS GPU-first local nếu có thoại; verify model/codec CUDA thật trước inference theo scope. Sinh WAV, đo duration sample rate/frames, tính lại timing FilmData, cue VTT/SRT; không dùng âm thanh ước lượng để đánh dấu sync hoàn thành. Không TTS thì skip có lý do. Không buộc user nghe từng đoạn.

## M4: mã cảnh thật

A: HTML/SVG/CSS/Canvas/GSAP paused `.seek(t)`, Three.js state theo t; mỗi shot `.html` có `window.film.frame(t)`. B: Remotion React TSX `useCurrentFrame()` / `interpolate` / `Sequence`, có thể dùng R3F/Three.js; các scene được render theo frame, không theo timer nondeterministic. Cảnh thực, không placeholder. Không buộc dùng cả 2D và 3D.

## M5–M7: timeline, render, bàn giao

A: `film.html` là timeline, chạy CLI đã xác minh trong cwd dự án, log argv/stdout/exit. B: Remotion Composition là timeline, giữ durationInFrames/fps và audio/subtitle tracks; render Remotion CLI/renderer có sẵn, log argv/stdout/exit. Không chạy OpenFilm previs hoặc fixture trong B chỉ để qua gate. Cả hai ghi `renders/V01.mp4`, FFprobe codec/streams/FPS/resolution/duration, FFmpeg decode để phát hiện lỗi và hash. Deliver V01 + source + manifest; không tự ghi `USER_ACCEPTED`. Feedback mục tiêu tạo V02/V03 riêng, bảo toàn V01. P18 smoke, P20 review chỉ kích hoạt chẩn đoán/user request.

## Legacy

Các hướng dẫn từng bắt ZIP ảnh trong M2 hoặc OpenFilm CLI trong Remotion Master là legacy. Với 99 template ID cũ, giữ ID nhưng xử lý packet dành cho engine khác bằng `SKIPPED_ENGINE_NOT_SELECTED` kèm skipReason và map đầu ra cùng chức năng bằng engine hiện tại; không tạo file giả.
