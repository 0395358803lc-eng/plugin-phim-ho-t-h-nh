---
name: openfilm-production-p06-p21
description: "Chạy P06–P21 để bàn giao V01 bằng OpenFilm CLI hoặc Remotion, storyboard dữ liệu, code-only mặc định, không bắt ảnh."
---

# P06–P21 v1.14.2 — Dual Engine + Data Storyboard

Mặc định `FINISH_FIRST_USER_REVIEW`: 8 macro M0–M7 và 99 packet IDs phục vụ kỹ thuật nội bộ, không xin xét duyệt mỗi packet, không thẩm mỹ QC trước video. Một approval scope đủ có thể bao phủ M1–M7; cài/download/model/CPU fallback/provider/phí/xóa/publish ngoài scope cần quyền riêng.

| Macro | Đầu ra cần có |
|---|---|
| M0 P00–P06 | Xác minh thiết bị, workspace, reuse, đúng runtime **engine đã chọn**. CLI OpenFilm chỉ bắt buộc với engine A; Remotion runtime chỉ với engine B. |
| M1 P07–P09 | Đọc bảy nguồn, chốt `masterEngine=openfilm|remotion`, FilmData frame nguyên; `.html` skeleton chỉ A, Composition skeleton chỉ B. |
| M2 P10–P11 | `storyboard.json`, `STORYBOARD.md`, style/character bible dữ liệu, SVG/CSS/TSX/geometry/code assets thực. Không ảnh storyboard, ZIP, Canvas Make. |
| M3 P12–P13 | WAV VieNeu GPU nếu cần giọng, đo duration thật, VTT/SRT. |
| M4 P14–P16 | Mã cảnh thật: `.html`/GSAP/Three.js cho A hoặc `.tsx`/React/R3F cho B; không placeholder cuối. |
| M5 P17–P18 | Một timeline master theo engine, P18 smoke tùy chọn khi lỗi hoặc yêu cầu. |
| M6 P19–P20 | Render `renders/V01.mp4` bằng **đúng engine**, kiểm file; P20 chỉ sau user feedback. |
| M7 P21 | Bàn giao V01, source/WAV/subtitles/manifest; user đánh giá rồi ghi USER_ACCEPTED hoặc REVISION_REQUESTED. |

Hợp đồng P10 đọc `openfilm-storyboard-data` và `references/STAGE_DEFINITIONS.json`. `FILE_DATA_STORYBOARD` luôn dùng, không kích hoạt `openfilm-image-zip-handoff`. Nếu ảnh từ ngoài không có, ghi `SKIPPED_NOT_REQUIRED` thay vì dừng. Nếu `masterEngine=remotion`, mọi template OpenFilm-only SKIP theo engine có skipReason và evidencePaths hợp lệ; không coi thiếu `film.html` hay OpenFilm CLI là lỗi. Nếu `masterEngine=openfilm` thì ngược lại, không đòi Composition/Remotion.

`OUTPUT_READY`: file thật tồn tại, decode/parse dùng được, hash đúng; `DELIVERED_FOR_REVIEW`: video đã giao; `USER_ACCEPTED`: chỉ người dùng đồng ý. Scheduler dùng `approvedScopeSha256`, stateRevision, outputPaths là file riêng, checkpoint atomic và chính sách tiếp tục không chạy nền. Lỗi file phụ thuộc chặn đúng bước, không chấm thẩm mỹ. Sau feedback giữ V01/hash, sửa đúng shot/dialogue targetIds, render V02 riêng; không tự publish.

`references/PRODUCTION_PLAYBOOK.md` mô tả cụ thể nhánh OpenFilm và Remotion. Các hướng dẫn legacy `CLI_REQUIRED` cho cả hai engine hoặc `ZIP ảnh P11` được chính sách v1.14.2 thay thế.
