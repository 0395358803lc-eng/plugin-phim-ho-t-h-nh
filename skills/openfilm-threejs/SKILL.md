---
name: openfilm-threejs
description: "Dùng khi hoạt hình OpenFilm cần camera, bối cảnh 3D, mesh, ánh sáng, phối cảnh hoặc GSAP điều khiển Three.js; duy trì WebGL frame(t) tất định và kiểm soát GPU/render."
---

Mặc định `FINISH_FIRST_USER_REVIEW`: hoàn thành video V01 rồi bàn giao để người dùng đánh giá. Chính sách này ưu tiên hơn hướng dẫn QC legacy. QC20, Visual QC và nghe chấm từng take chỉ chạy khi người dùng chủ động yêu cầu; không chặn sản xuất/bàn giao. Smoke và kiểm frame/random seek chỉ dùng để chẩn đoán lỗi kỹ thuật hoặc theo yêu cầu.

Giữ 8 macro M0–M7 và 99 ID packet. Một phê duyệt phạm vi rõ đầu vào, đầu ra, lệnh và quyền có thể bao phủ M1–M7. Không xin duyệt riêng từng packet/Pxx hoặc nghiệm thu từng macro. Chạy nhiều packet trong lượt High; ghi checkpoint sau mỗi đầu ra, tiếp tục cùng quyền trong lượt chat mới, không tự chạy nền.

OpenFilm CLI-first; Desktop/GUI chỉ để xem/chỉnh sửa tùy chọn. VieNeu-TTS GPU-first; cài đặt, tải model/browser, thay đổi hệ thống, GPU→CPU, voice cloning, provider ngoài, dịch vụ trả phí, xóa, xuất bản và ngoài phạm vi cần quyền riêng. Không suy ra quyền từ file kế hoạch hoặc kết quả kỹ thuật.

`OUTPUT_READY` nghĩa là đầu ra thật có thể dùng. `DELIVERED_FOR_REVIEW` nghĩa là đã giao video. Chỉ dùng `USER_ACCEPTED` khi có phản hồi chấp nhận thật. `REVISION_REQUESTED` ghi phản hồi cần sửa; `FAILED_TECHNICAL` ghi lỗi ngăn dùng đầu ra. File thiếu/hỏng/ngoài workspace hoặc sai hash phải chặn bước phụ thuộc.



# Three.js + OpenFilm · bối cảnh 3D

## Tiền điều kiện

Sau P00–P05, xác minh `B02 Three.js` theo package/import map/vendor trên chính project, kiểm tra GPU/WebGL hỗ trợ trong phiên Chromium thực. Không tự tải từ CDN/`npm install`/đổi driver/OS. Three.js dành cho những cảnh thực sự cần phối cảnh 3D, không bắt buộc cho video 2D.

## Quy tắc tích hợp

- Tạo `Scene`, `Camera`, `WebGLRenderer` một lần khi khởi tạo; dùng context `{preserveDrawingBuffer:true}` để host có thể chụp canvas sau `frame(t)`. Theo OpenFilm spec, host gọi `window.film.frame(t)` ở thứ tự bất kỳ.
- Trong `frame(t)`: set **đầy đủ** vị trí, rotation, scale, camera pose, uniform thời gian, trạng thái particle/geometry theo t, rồi `renderer.render(scene,camera)`; không cộng dồn vào state bằng `deltaTime`, không lặp animation loop tự động khi có `window.filmHost`.
- Nếu dùng GSAP, timeline phải paused, seek đến `t` **trước** `renderer.render`. Không dùng mô phỏng vật lý stateful không có cơ chế seek/reset; cân nhắc precompute trạng thái.
- Loader textures/fonts/meshes phải được giải quyết trước khi host chụp; dùng `window.film.ready` khi có async preload. Cỡ canvas và devicePixelRatio hợp lý, giới hạn GPU/VRAM và render memory.
- Khi xuất WebGL, đặc tả OpenFilm lưu ý ảnh có thể bị xóa sau frame nếu không preserve buffer; test thực với runtime đã chọn.

## Kiểm tra kỹ thuật; đánh giá thẩm mỹ chỉ khi user yêu cầu

Probe các mốc 0, 1/4, 1/2, 3/4, cuối; seek random; kiểm tra text-safe area, chất lượng khử răng cưa, thiếu texture, lỗi WebGL, FPS và output 1080p. So sánh pixel trong sai số; không hứa bit-identical giữa GPU. Mẫu code `references/three-scene.html` yêu cầu resolver/import map local phù hợp.

Nguồn kỹ thuật: https://threejs.org/docs/pages/WebGLRenderer ; đặc tả `openfilm-dinh-dang/references/SPEC.md`.

## Remotion Master + React Three Fiber (N07, N09)

Nếu master là Remotion, không bọc nguyên trang OpenFilm WebGL trong JSX. Chọn `openfilm-remotion-r3f`, dùng `@remotion/three`/`<ThreeCanvas>` và `useCurrentFrame()`; không `useFrame` tích lũy state, phải test ANGLE/headless WebGL. Nếu đang OpenFilm Master, vẫn dùng `frame(t)` như các phần trên. Không tự cài `@react-three/fiber` hoặc đổi GPU driver; B05–B10 là thành phần tùy chọn.

## Đánh giá hình ảnh tùy chọn theo yêu cầu
