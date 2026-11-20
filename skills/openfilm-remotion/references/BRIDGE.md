# Remotion → OpenFilm bridge (tùy chọn)

Remotion và OpenFilm sử dụng hai cấu trúc dự án khác nhau. Bridge có chủ đích là **media file trung gian**, không phải chuyển đổi nguyên trạng React/JSX thành `film.html`.

## Mẫu kế hoạch

1. Trước build/render: xác minh P00–P05 và phê duyệt giai đoạn sản xuất. Ghi `source project`, lockfile, commit/file hash, `composition ID`, aspect ratio, FPS, tổng frames.
2. Tạo `Composition` theo mẫu React/Remotion đã khóa phiên bản. Ví dụ `frame = useCurrentFrame()`; nội suy `opacity` và `transform` theo frame, không theo wall clock.
3. Gọi `renderMedia()` từ `@remotion/renderer` hoặc CLI Remotion **đã cài**, với output path trong `<WORKSPACE>/renders/intermediate/clip-xxx.mp4`. Cú pháp/codec/options xác minh theo version hiện tại, không dùng `npx` fallback tải package.
4. FFprobe metadata trước import: codec, duration, size, avg_frame_rate, audio streams. So sánh với storyboard: thời gian `durationInFrames / fps`.
5. Bố trí file theo thư mục project để OpenFilm tham chiếu hợp lệ, không phụ thuộc file tạm có thể bị xóa. Nghiệm thu video/âm thanh rồi thêm `<video src="assets/intermediate/clip-xxx.mp4#t=0,4">` vào track trong `film.html` theo OpenFilm SPEC. Không chạm asset nguồn.
6. Nếu clip không đạt: quay về Remotion sửa và render lại vào **file phiên bản mới**, không ghi đè clip đã nghiệm thu mà chưa có phê duyệt.

Chỉ chọn Remotion khi lợi ích rõ (template React, clip hàng loạt, JSX animations); nếu GSAP/Three.js trực tiếp trong OpenFilm đáp ứng thì tránh renderer chồng chéo và bỏ qua B03.
