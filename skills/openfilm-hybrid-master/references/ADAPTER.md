# Hợp đồng adapter OpenFilm ↔ Remotion (chỉ trao đổi qua file)

Cấu trúc trong `<WORKSPACE>/projects/<film-id>/`:

- `openfilm/film.html`, `openfilm/scenes/`, `openfilm/assets/`
- `scene-data/film.json`, `scene-data/assets-manifest.json`
- `renders/previs/openfilm-previs.mp4` (tùy chọn)
- `remotion/public/audio|images|models/`, `remotion/src/...` (chỉ khi Remotion Master)
- `renders/intermediate/` và `renders/master/`

**Bất biến:** thời gian 0-based, half-open `[startFrame, startFrame+durationInFrames)`; FPS duy nhất và số frame không âm; đường dẫn media trong JSON tương đối với project root, ngăn `..`/đường dẫn tuyệt đối; `source_sha256` nếu có phải đo từ artifact thật. OpenFilm `frame(t)` theo giây; Remotion dùng `useCurrentFrame()`, chuyển `t=frame/fps`; không tích lũy biến theo thứ tự render. Không đồng bộ thời gian bằng ước lượng ký tự TTS.

Trong chiều OpenFilm → Remotion, chỉ handoff hình ảnh đã render hoặc assets được phép tái dùng cùng timing **do người dựng xác nhận**; không giả định rằng xuất phim tự tạo sẵn JSON. `OffthreadVideo` đọc reference MP4 trong `public/` nếu cần; bỏ khỏi master khi chỉ để đối chiếu.

Chiều Remotion → OpenFilm, xuất clip `N` frames ở `F` fps; đo bằng FFprobe, so sánh với `(N/F)` trong dung sai frame/codec, copy bằng thao tác được duyệt sang thư mục nguồn của phim, nhập `<video>` bằng đường dẫn tương đối. Khi có âm thanh thoại trên master chỉ có **một** bản audio active; clip trung gian có track thoại thì tránh duplicate mix.

Điều kiện import: (1) file thực tồn tại; (2) quyền đọc/giấy phép; (3) codec/size/fps/duration kiểm tra; (4) nguồn hash/file provenance được ghi; (5) người dùng đã phê duyệt giai đoạn dựng và vị trí ghi. Không cài dependency hay render trong P03–P05.
