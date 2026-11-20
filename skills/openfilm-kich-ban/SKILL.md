---
name: openfilm-kich-ban
description: "Chuyển kịch bản thành beats, shot list và storyboard dữ liệu JSON/Markdown/FilmData, không tạo ảnh."
---

# Kịch bản và storyboard DATA_ONLY v1.14.2

Nhận 7 tài liệu nguồn theo `openfilm-script-input`, giữ nội dung nguồn bất biến. Phân beat, mục tiêu cảm xúc, thoại/tường thuật, hành động quan sát được, góc máy, nhịp, SFX, transition và duration theo integer frames. Shot list `shotId`, `sceneId`, `startFrame`, `durationInFrames`, characters, action, layout, camera, lighting, motion, dialogueIds, subtitleIds, SFX, assetRefs, implementation; mọi shot map 1:1 FilmData.

P10 tạo `storyboard/storyboard.json` và `storyboard/STORYBOARD.md`, mỗi shot nêu bố cục/vị trí nhân vật/trạng thái biểu cảm/camera path/keyframes/chuyển động/vật thể/bối cảnh. Character bible mô tả dáng, trang phục, màu, tỷ lệ, phụ kiện bằng dữ liệu; style bible quy định palette, camera, ánh sáng, typography. **Không gọi tạo ảnh portrait/fullBody/expressions/turnaround16 hay ảnh storyboard, không Canvas Make/Make all/ZIP.** Mô hình nhân vật/đạo cụ/bối cảnh được viết bằng SVG/CSS/Three.js geometry/TSX-R3F ở giai đoạn dựng cảnh, không phải PNG storyboard.

Đọc `openfilm-storyboard-data` để kiểm dữ liệu, sau đó `openfilm-hybrid-master` để đi một trong hai nhánh. A OpenFilm tạo `.html`, B Remotion tạo `.tsx`/Composition; không ép B tạo HTML. Chỉ đánh giá pixel khi user yêu cầu xem **frame của bản render thật**. Việc không có ảnh storyboard tuyệt đối không phải `VISUAL_BLOCKED` hay lý do dừng M2.

Mục tiêu cuối: V01 dùng được, user nghiệm thu sau bàn giao. Giữ checkpoint, hash output thực, quyền đặc biệt riêng.
