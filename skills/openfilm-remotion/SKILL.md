---
name: openfilm-remotion
description: "Dùng khi cần Remotion Master dựng/encode cuối hoặc clip React trung gian cho OpenFilm Master; P00–P05, phê duyệt master và file adapter bắt buộc."
---

# Remotion Master hoặc Remotion clip → OpenFilm Master · hai chế độ

## Vị trí trong hệ thống

Remotion là engine React **độc lập**. **OpenFilm Master**: Remotion tạo clip trung gian, OpenFilm làm timeline/biên tập/hậu kỳ cuối. **Remotion Master**: OpenFilm làm previs/asset/shot planning, Remotion làm timeline master/encode; mọi handoff qua asset, MP4 và FilmData file được kiểm, không có API OpenFilm → JSX trực tiếp. Chỉ bật Remotion khi người dùng chọn mode/template/batch, P00–P05 đã duyệt và B03/B05–B10 đủ môi trường; nếu không đánh dấu `TÙY CHỌN CHƯA KÍCH HOẠT`.

## Chuỗi làm việc đã duyệt

1. Sau P00–P05, kiểm tra `B03 Remotion`, Node.js runtime, React, `remotion`, `@remotion/renderer` hoặc CLI, Chromium/FFmpeg phù hợp và giấy phép sử dụng theo dự án. Chỉ dùng environment đã chứng minh tương thích; phiên bản package khóa trong lockfile, **không `npx` tự tải**.
2. Khi đã có phê duyệt tạo clip, xác nhận `Composition` với width/height/fps/durationInFrames, các input props và assets cục bộ; `useCurrentFrame()` để hoạt hình theo thời gian frame, không dựa vào state ngẫu nhiên hoặc timer.
3. Render intermediate vào `<WORKSPACE>/renders/intermediate`, không viết vào assets gốc; dùng CLI **đã xác minh được cài** trong project hoặc API `@remotion/renderer` theo phiên bản hiện tại. Kiểm tra output tồn tại, metadata bằng FFprobe, tránh trùng tiếng/âm thanh, giữ thông tin FPS/resolution/duration.
4. Import clip hợp lệ vào media/timeline OpenFilm qua đường dẫn tương đối thuộc dự án hoặc đường dẫn đã được phê duyệt. Sau đó kiểm tra lại cut, sync phụ đề/voiceover, color, audio và export tổng bằng OpenFilm.
5. Cảnh đã dựng thành MP4 sẽ không còn edit được như JSX bên trong Studio. Giữ project React và build metadata trong workspace để có thể sửa và render lại khi cần.

## Reuse và QC

Tìm Remotion trong workspace cũ trước; `node_modules`/path/ABI có thể không portable, cần version-lock/Node compatibility thực. Không auto copy, global install, đổi PATH, tải Chromium hoặc tự kích hoạt Remotion từ một yêu cầu không cần React. Các clip chỉ được dùng sau khi có nghiệm thu hình/âm thanh và kiểm tra clip duration có khớp timeline.

Nguồn: https://www.remotion.dev/docs/api và https://www.remotion.dev/docs/renderer/render-media . Xem `references/BRIDGE.md`.

## Remotion Master — mở rộng N01–N18

Nếu master `remotion`, trước khi biên tập đọc `openfilm-hybrid-master`, `openfilm-filmdata`, `openfilm-remotion-r3f`, `openfilm-audio-subtitles`, `openfilm-render-profiles`, `openfilm-qc-advanced`. `FilmData` là nguồn timeframe duy nhất; scenes dùng `useCurrentFrame()` và phụ đề/voice dùng integer frames. Bộ `@remotion/three` chỉ sử dụng nếu B06/B07/GPU/WebGL khả dụng; `Config.setChromiumOpenGlRenderer('angle')` chỉ sau khi kiểm chứng theo version. `npx remotion` có thể auto tải trong môi trường thiếu, không dùng ở P04. Render `master` bằng Remotion khi đã duyệt, không import ngược trừ khi cần mở rộng OpenFilm. Kiểm tra codec/chiều cao/chiều rộng/FPS/AAC/FFprobe và đủ QC20 trước khi tuyên bố PASS. Đối chiếu `references/BRIDGE.md` và `openfilm-hybrid-master/references/ADAPTER.md`.
