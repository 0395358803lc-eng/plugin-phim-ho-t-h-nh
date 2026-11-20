---
name: openfilm-remotion-r3f
description: "Tích hợp Three.js/React Three Fiber với @remotion/three trong Remotion Master, khử lỗi WebGL/ANGLE và đồng bộ hình theo frame." 
---

# React Three Fiber + Remotion Master (N07, N09)

Chỉ dùng khi `masterEngine=remotion`, P00–P05 đã kiểm, chế độ Remotion Master/tiến hành dựng **được phê duyệt** và B03/B05–B10 có runtime hợp lệ. Nếu `masterEngine=openfilm`, dùng `openfilm-threejs` với `window.film.frame(t)`, không buộc có R3F.

## Bản đồ dependencies theo chế độ

- React/React DOM, `three`, `@react-three/fiber`, `@remotion/three`, `remotion`, `@remotion/cli` hoặc renderer, `@types/three` khi TS, TypeScript. Phiên bản phải tương thích từ lockfile đã kiểm; không tự `npx create-video@latest`, tải Chromium hoặc cài toàn cục.
- `<ThreeCanvas width={width} height={height} camera={{...}}>` là canvas của scene React 3D. `useCurrentFrame()`/`useVideoConfig()` lấy frame/fps, tính **trực tiếp** transform/material/camera từ frame/seed cố định, không dùng `useFrame` tăng state `+=`, timers hay `Math.random()` không seed.
- Khi sử dụng `<Sequence>` bên trong R3F tree, cần `layout="none"` để tránh phần tử `<div>` không hợp lệ; xem ví dụ trong báo cáo. Đọc API theo phiên bản cài đặt thật để không trộn API khác major.
- WebGL headless: kiểm tra ANGLE, WebGLContext, shader/model/texture, khả năng tải/ready, kích thước frame. Khi phù hợp và version hỗ trợ, Remotion config có `Config.setChromiumOpenGlRenderer('angle')`; đây là cấu hình cần **thử nghiệm**, không đảm bảo GPU hoạt động. Không tắt sandbox/bảo mật hay đổi driver nếu chưa được phê duyệt.

## QC

1. Chụp frame đầu/giữa/cuối, cả các frame random thứ tự không tăng dần; cảnh không nhảy, không đen, không thiếu texture.
2. Không đưa model GLB/texture từ URL ngoài vào nếu chưa tải, license, hash và duyệt. Giới hạn texture/VRAM theo máy.
3. R3F test nhỏ 5 giây trước khi render nhiều phút; nếu WebGL fail → `BLOCKED`, nêu log và phương án giảm complexity/concurrency, không tuyên bố render thành công.
4. Mẫu thiết kế TSX trong `references/R3F_EXAMPLE.tsx` cần thay nội dung/phụ thuộc theo runtime, không phải build đã xác minh.
