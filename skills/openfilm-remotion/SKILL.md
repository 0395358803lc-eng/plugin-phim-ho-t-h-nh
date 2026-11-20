---
name: openfilm-remotion
description: "Remotion Master độc lập: từ FilmData/storyboard dữ liệu viết TSX/React/Composition rồi render V01, không cần OpenFilm CLI."
---

# Remotion Master — v1.14.2

Remotion là engine ngang hàng OpenFilm CLI, chọn tại P08, không phải chỉ là clip phụ trợ hoặc fallback. `masterEngine=remotion` thì các bước chính đều thực hiện bằng code React/TSX/Remotion. Không buộc chạy OpenFilm CLI, tạo film.html, OpenFilm previs, canvas, look hay render bằng OpenFilm. Một workflow hybrid chỉ khi user yêu cầu đặc biệt.

P00–P06 xác minh đúng Node.js, React, Remotion packages/renderer/CLI, browser và FFmpeg nếu profile cần; reuse từ workspace đã duyệt; không tự npx/install/download. P09 lập FilmData và Composition skeleton. P10 tạo **storyboard JSON + Markdown** (không PNG); P11 chỉ chuẩn bị code SVG/TSX, vector/geometry/R3F và media có sẵn người dùng cấp. P12/P13 WAV VieNeu GPU và timing, P14–P16 `.tsx` scenes thực, `useCurrentFrame()`, `interpolate()`, GSAP theo frame hoặc R3F; P17 Composition master với Sequence/Audio/caption đồng bộ; P19 `remotion render` hoặc `@remotion/renderer` đã xác minh tạo V01.mp4; P21 FFprobe/decode/hash và bàn giao.

Các packet OpenFilm-only được đánh dấu `SKIPPED_ENGINE_NOT_SELECTED` với lý do chứ không tạo file OpenFilm giả. Các packet chung, đặc biệt FilmData/P10/P11/WAV/render và manifest, vẫn bắt buộc. Chỉ tạo ảnh nếu user riêng biệt yêu cầu một asset ảnh có mục đích hiển thị trong phim; không có ảnh storyboard mặc định, không ZIP handoff mặc định. Không đòi QC thẩm mỹ từng cảnh; V01 trước, user đánh giá sau.
