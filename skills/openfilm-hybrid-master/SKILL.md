---
name: openfilm-hybrid-master
description: "Chọn OpenFilm Master hoặc Remotion Master sau P00–P05; tổ chức handoff dựa trên file, giữ một timeline và không tự cài hoặc đổi engine." 
---

# Hai chế độ master (N01–N02)

**Trước hết** chạy `video-hoat-hinh` P00–P05 theo đúng thứ tự máy → thư mục → workspace → reuse → audit → danh sách phê duyệt. Không dùng yêu cầu hybrid làm lý do tự mở Remotion, chạy `npx` hoặc cài môi trường. Chỉ chọn chế độ khi đã có dữ liệu dự án và sự đồng ý riêng cho giai đoạn sản xuất; nếu chưa rõ, mặc định **OpenFilm Master** vì tương thích với các dự án cũ.

| Quyết định | OpenFilm Master (mặc định) | Remotion Master (tùy chọn) |
|---|---|---|
| Nguồn timeline cuối | `film.html`, OpenFilm Studio/CLI | `FilmData` + Remotion Composition |
| Dựng 2D/3D | HTML/SVG/GSAP và Three.js điều khiển `window.film.frame(t)` | React/GSAP `useCurrentFrame()`, `@remotion/three` / React Three Fiber |
| VieNeu-TTS | WAV làm `<audio>` track trong `film.html` | WAV trong audio track `Sequence`/`Audio` của Remotion |
| Kết xuất cuối | OpenFilm CLI/Studio có sẵn | Remotion CLI/renderer có sẵn |
| Giấy phép/khả năng vận hành | Kiểm OpenFilm + runtime cần thiết | Kiểm `B03, B05–B10`, Chromium, license Remotion, audio, WebGL |

**Không có API trực tiếp đã xác minh để chuyển `film.html` thành JSX**. Adapter là các file giao tiếp có manifest, không copy source code tùy tiện. Từ OpenFilm sang Remotion: xuất `previs.mp4`/ảnh tham chiếu (chỉ sau duyệt), `assets/`, `scene-data/film.json` (thời gian do biên tập xác nhận). Remotion dùng `staticFile()` cho những file dưới `public/`; không tham chiếu tuyệt đối ổ Windows vào bundle. Từ Remotion về OpenFilm: xuất MP4 trung gian và nạp video vào `film.html` nếu chế độ này được chọn, không đưa JSX trực tiếp vào OpenFilm.

1. **MASTER_SELECTION:** trình lựa chọn A/B, nêu khác biệt editability, dependency, license, tài nguyên. Chưa được duyệt thì không đổi chế độ/ngẫu nhiên cài Remotion.
2. **SOURCE_LOCK:** lưu `master_engine`, FPS, kích thước, scene data, đường dẫn asset, lockfile, license, provenance vào manifest. Bảo vệ nguồn gốc, không ghi đè artifact đã nghiệm thu.
3. **CONTRACT:** đọc `openfilm-filmdata`, dùng cùng `film.json`/`assets-manifest.json`; tất cả shot có startFrame và durationInFrames chính xác, 0-based half-open [start,end).
4. **PREVIS:** OpenFilm render preview có kiểm chứng khi cần; `previs.mp4` là reference, không là dependency bắt buộc của final.
5. **HANDOFF:** adapter kiểm tra đường dẫn relative, file tồn tại/codec/FPS và mapping từ time(s) sang frame trước khi import. Chỉ chuyển audio/media qua một timeline master để tránh tiếng lặp.
6. **FAILOVER:** Remotion thiếu điều kiện → không tự sửa cài, có thể đề xuất chuyển về OpenFilm Master **sau khi được chấp thuận**.
7. **QC:** so sánh thời lượng, cut/shot, voice/subtitles, frame ngẫu nhiên, ảnh trước/sau handoff; báo PASS/FAIL/BLOCKED dựa trên bằng chứng.

Tham chiếu `references/ADAPTER.md` và `openfilm-filmdata/SKILL.md`. Nguồn khái niệm: báo cáo `deep-research-report (1).md`, phần kiến trúc và ranh giới file adapter. Kỹ năng không tuyên bố một tích hợp engine tự động đã tồn tại.

## OpenFilm runtime & bootstrap v1.8.0

Dù master OpenFilm hay Remotion, nếu dùng OpenFilm để previs/preview thì P06 phải có capability openProject+inspectFrame VERIFIED hoặc báo BLOCKED cho nhánh OpenFilm. P09 tạo OpenFilm skeleton cho previsualization từ FilmData trước P16. Với Remotion Master, không đòi OpenFilm phải render final; E2E OpenFilm độc lập P06 nếu OpenFilm render được, nếu không báo rõ không kiểm chứng được chứ không dùng Remotion output để báo OpenFilm PASS. Canvas optional; giọng VieNeu chỉ import WAV theo voice lock.

## CLI-first runtime v1.9.0

Mọi công đoạn OpenFilm của cả hai chế độ master bắt buộc dùng **OpenFilm CLI A02** (`openfilm-cli-execution`). OpenFilm Desktop chỉ là viewer tùy chọn; không có CLI thì P06 BLOCKED và phải xin duyệt cài/reuse, không fallback UI-only. OpenFilm Master dùng `look`/`render` xuất final; Remotion Master dùng OpenFilm CLI để inspect/render previs rồi Remotion CLI xuất final. Mọi `look/render` chạy tại cwd chứa film.html theo profile và có CLI event + QC evidence.
