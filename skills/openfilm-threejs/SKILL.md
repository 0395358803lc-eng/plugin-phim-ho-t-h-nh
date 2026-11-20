---
name: openfilm-threejs
description: "Dùng khi hoạt hình OpenFilm cần camera, bối cảnh 3D, mesh, ánh sáng, phối cảnh hoặc GSAP điều khiển Three.js; duy trì WebGL frame(t) tất định và kiểm soát GPU/render."
---

# Three.js + OpenFilm · bối cảnh 3D

## Tiền điều kiện

Sau P00–P05, xác minh `B02 Three.js` theo package/import map/vendor trên chính project, kiểm tra GPU/WebGL hỗ trợ trong phiên Chromium thực. Không tự tải từ CDN/`npm install`/đổi driver/OS. Three.js dành cho những cảnh thực sự cần phối cảnh 3D, không bắt buộc cho video 2D.

## Quy tắc tích hợp

- Tạo `Scene`, `Camera`, `WebGLRenderer` một lần khi khởi tạo; dùng context `{preserveDrawingBuffer:true}` để host có thể chụp canvas sau `frame(t)`. Theo OpenFilm spec, host gọi `window.film.frame(t)` ở thứ tự bất kỳ.
- Trong `frame(t)`: set **đầy đủ** vị trí, rotation, scale, camera pose, uniform thời gian, trạng thái particle/geometry theo t, rồi `renderer.render(scene,camera)`; không cộng dồn vào state bằng `deltaTime`, không lặp animation loop tự động khi có `window.filmHost`.
- Nếu dùng GSAP, timeline phải paused, seek đến `t` **trước** `renderer.render`. Không dùng mô phỏng vật lý stateful không có cơ chế seek/reset; cân nhắc precompute trạng thái.
- Loader textures/fonts/meshes phải được giải quyết trước khi host chụp; dùng `window.film.ready` khi có async preload. Cỡ canvas và devicePixelRatio hợp lý, giới hạn GPU/VRAM và render memory.
- Khi xuất WebGL, đặc tả OpenFilm lưu ý ảnh có thể bị xóa sau frame nếu không preserve buffer; test thực với runtime đã chọn.

## QC

Probe các mốc 0, 1/4, 1/2, 3/4, cuối; seek random; kiểm tra text-safe area, chất lượng khử răng cưa, thiếu texture, lỗi WebGL, FPS và output 1080p. So sánh pixel trong sai số; không hứa bit-identical giữa GPU. Mẫu code `references/three-scene.html` yêu cầu resolver/import map local phù hợp.

Nguồn kỹ thuật: https://threejs.org/docs/pages/WebGLRenderer ; đặc tả `openfilm-dinh-dang/references/SPEC.md`.

## Remotion Master + React Three Fiber (N07, N09)

Nếu master là Remotion, không bọc nguyên trang OpenFilm WebGL trong JSX. Chọn `openfilm-remotion-r3f`, dùng `@remotion/three`/`<ThreeCanvas>` và `useCurrentFrame()`; không `useFrame` tích lũy state, phải test ANGLE/headless WebGL. Nếu đang OpenFilm Master, vẫn dùng `frame(t)` như các phần trên. Không tự cài `@react-three/fiber` hoặc đổi GPU driver; B05–B10 là thành phần tùy chọn.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate
Shot 3D M4 cần **ChatGPT quan sát hình render thực**, kiểm góc camera, clipping, vật liệu, texture, shading, lighting, model pose và frame-boundary. WebGL log, screenshot path hoặc manifest 3D tự nó không được PASS; đưa ảnh OpenFilm CLI look thực vào model theo `openfilm-visual-inspection`.
