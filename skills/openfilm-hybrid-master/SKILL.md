---
name: openfilm-hybrid-master
description: "Chọn một trong hai engine ngang hàng OpenFilm CLI hoặc Remotion, mỗi engine render V01 độc lập từ FilmData và storyboard dữ liệu."
---

# Dual master engines v1.14.2

P00–P05: xác minh máy, workspace, reuse và dependencies trong phạm vi đã duyệt. P08 chốt **A OpenFilm CLI** hay **B Remotion** (người dùng đã chọn thì giữ), ghi `masterEngine=openfilm|remotion` vào FilmData và production profile. Không mặc định chuyển engine, không cài tự động. Nếu user chọn B chỉ kiểm runtime Node/React/Remotion renderer/CLI và Chromium/FFmpeg theo nhu cầu; **không yêu cầu A02 OpenFilm CLI**. Nếu chọn A chỉ kiểm OpenFilm CLI và dependencies thực sự cần; không yêu cầu Remotion B03/B05–B10.

| Thuộc tính | A: OpenFilm CLI | B: Remotion |
|---|---|---|
| Sản xuất cảnh | HTML/CSS/SVG/Canvas/GSAP/Three.js + `window.film.frame(t)` | TSX/React, `useCurrentFrame()`, `Sequence`, GSAP/R3F/Three.js nếu cần |
| Dữ liệu storyboard | JSON + Markdown + FilmData, không ảnh | JSON + Markdown + FilmData, không ảnh |
| Timeline master | `film.html` | Remotion Composition |
| Giọng/nhạc/phụ đề | WAV/audio tracks và captions | `Audio`/Sequence/captions theo frames |
| Render cuối | `openfilm render` CLI | Remotion CLI hoặc @remotion/renderer |
| Runtime bắt buộc | CLI OpenFilm đã xác minh | Remotion, React, Node, renderer/browser cần thiết |

Hợp đồng chung: shots với `shotId`, `startFrame`, `durationInFrames`, dialogue/asset manifest; không overlap/gap ngoài chủ ý. Asset mặc định được tạo bằng code, không cần PNG storyboard, ZIP, Canvas nodes hay OpenFilm preview. Có thể dùng clip trung gian từ engine khác **chỉ khi người dùng chọn hybrid**, xác minh file; không mặc định dùng chéo hai engine. Khi một engine thiếu dependency, báo thiếu và đề xuất phương án; không im lặng đổi engine.

Engine B: P09.06 OpenFilm `film.html`/placeholder, P10 Canvas, P14.06 OpenFilm HTML replacement, P16 OpenFilm preview, P18 OpenFilm smoke, P19 OpenFilm render event phải là `SKIPPED` với `skipReason=SKIPPED_ENGINE_NOT_SELECTED` và `evidencePaths` có tệp quyết định engine thật nếu có template riêng; thay thế bằng Composition source, TSX scenes, Remotion render evidence theo cùng stage. Engine A tương tự SKIP packet Remotion-only. Chỉ user mới được chọn/thay master. Trong v1.14.2, các câu legacy "CLI-required cả hai master" và "Remotion phải qua OpenFilm previs" bị vô hiệu cho nhánh B.

Mặc định Finish First: render V01, kiểm file/stream/FFprobe, giao xem; QC thẩm mỹ chỉ theo yêu cầu, giữ V01 khi làm V02/V03. Các thao tác đặc biệt (cài/download/provider/phí/xóa/publish/CPU fallback) luôn cần quyền riêng ngoài scope nếu chưa cấp.
