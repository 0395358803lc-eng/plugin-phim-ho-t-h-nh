---
name: openfilm-animation
description: "Thiết kế và viết hoạt hình khung hình tất định bằng HTML, SVG, Canvas/WebGL, CSS, JavaScript cho OpenFilm; định tuyến khi cần GSAP cho 2D, Three.js cho 3D hoặc Remotion cho clip React riêng."
---

# Dựng cảnh OpenFilm theo `window.film.frame(t)`

Đọc `openfilm-dinh-dang` trước. Mọi shot là trang HTML, khung hình ở thời điểm `t` phải có thể dựng lại khi seek bất kỳ thứ tự nào. Không cập nhật bằng `deltaTime`/RAF/interval trong host. Dùng `film.html` để ghép shot, âm thanh và video.

## Engine lựa chọn

- Cảnh 2D đơn giản: DOM, SVG, CSS, Canvas 2D; thiết lập trạng thái trực tiếp bằng `t`.
- Cảnh 2D động phức tạp (nhân vật, chữ, hiệu ứng): đọc `openfilm-gsap/SKILL.md`, dùng timeline GSAP **paused** và `.seek(t)` từ `frame(t)`; xác minh đảo chiều/seek không phụ thuộc trạng thái trước.
- Camera, mesh 3D, ánh sáng: đọc `openfilm-threejs/SKILL.md`, set trạng thái từ `t`, gọi `renderer.render(scene,camera)` trực tiếp trong `frame(t)` và WebGL với `preserveDrawingBuffer` nếu chụp frame.
- Khi cần cả GSAP + Three.js: GSAP điều khiển thuộc tính 3D từ timeline đã pause; gọi seek sau đó render Three.js trong cùng `frame(t)` và kiểm nghiệm seek ngẫu nhiên. Cân nhắc tính tất định và chi phí GPU.
- React composition/production batch: đọc `openfilm-remotion/SKILL.md`; render clip trung gian riêng **sau phê duyệt**, rồi chèn media có đường dẫn hợp lệ trong OpenFilm. Không nhập JSX trực tiếp vào `window.film` hay khẳng định tích hợp runtime sẵn.

## Dựng shot và âm thanh

Một shot một `scenes/shot-xxx.html`; asset cục bộ/tương đối trong `assets` hoặc vendor cục bộ thuộc project sau phê duyệt. Nhân vật SVG/DOM tách layer có thể chỉnh được. Tránh lạm dụng `left/top` trên clip; ưu tiên thuộc tính transform/translate/rotate/scale theo đặc tả, không phá track khóa hoặc overrides Studio. Âm thanh trong `<audio>` track của `film.html`, không chơi autoplay từ cảnh khi host render. Captions/WebVTT khi có nguồn thực.

## Nghiệm thu

Render/scrub cùng `t` nhiều lần (thứ tự t ngẫu nhiên), kiểm tra đầu/giữa/cuối và sát điểm cut; so hình bằng dung sai hợp lý (WebGL có thể sai khác pixel giữa GPU), QC media path, FPS, khung 16:9/9:16, font và text safe area. Chỉ đánh dấu PASS nếu có bằng chứng thực từ máy hoặc file kiểm thử.

## Early skeleton v1.8.0

Mã cảnh OpenFilm được viết **đè có kiểm soát vào bản working copy** của scene sau khi người dùng duyệt. P09 tạo các placeholder `scenes/<shot-id>.html` và `film.html` theo FilmData. P14.06 kiểm từng scene có code thật, thay placeholder bằng bản cảnh được duyệt, giữ `film.html` và các track người dùng đã chỉnh; P16.06 phải FAIL/BLOCKED nếu còn placeholder. Không tạo `film.html` lần đầu ở P17. Đọc `openfilm-runtime-control/references/EARLY_PROJECT.md`.

## Đường kiểm tra OpenFilm CLI v1.9.0

Viết HTML/SVG/GSAP/Three.js theo `frame(t)` từ code/FilmData; để nghiệm thu shot, dùng **OpenFilm CLI** `openfilm look` từ cwd chứa `film.html` đã được P09 bootstrap và được P06 xác minh. Không dùng OpenFilm Desktop UI thay cho lệnh; Studio chỉ tùy chọn xem. Mỗi thao tác thuộc work packet/approval, log và ảnh đầu/giữa/cuối.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate
M4 không ghi nhận chất lượng hình chỉ từ `window.film.frame(t)` hoặc source review. Phải trích ảnh thật `openfilm look` ở START/Q1/MID/Q3/END mỗi shot, đưa vào lượt ChatGPT dưới dạng image content, tự xem lỗi/tính nhất quán và ghi Visual QC; thấy lỗi thì sửa trong scope rồi xem lại. Chi tiết skill `openfilm-visual-inspection`.
