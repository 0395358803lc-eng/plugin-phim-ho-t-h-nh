---
name: openfilm-animation
description: "Thiết kế và viết hoạt hình khung hình tất định bằng HTML, SVG, Canvas/WebGL, CSS, JavaScript cho OpenFilm; định tuyến khi cần GSAP cho 2D, Three.js cho 3D hoặc Remotion cho clip React riêng."
---

Mặc định `FINISH_FIRST_USER_REVIEW`: hoàn thành video V01 rồi bàn giao để người dùng đánh giá. Chính sách này ưu tiên hơn hướng dẫn QC legacy. QC20, Visual QC và nghe chấm từng take chỉ chạy khi người dùng chủ động yêu cầu; không chặn sản xuất/bàn giao. Smoke và kiểm frame/random seek chỉ dùng để chẩn đoán lỗi kỹ thuật hoặc theo yêu cầu.

Giữ 8 macro M0–M7 và 99 ID packet. Một phê duyệt phạm vi rõ đầu vào, đầu ra, lệnh và quyền có thể bao phủ M1–M7. Không xin duyệt riêng từng packet/Pxx hoặc nghiệm thu từng macro. Chạy nhiều packet trong lượt High; ghi checkpoint sau mỗi đầu ra, tiếp tục cùng quyền trong lượt chat mới, không tự chạy nền.

OpenFilm CLI-first; Desktop/GUI chỉ để xem/chỉnh sửa tùy chọn. VieNeu-TTS GPU-first; cài đặt, tải model/browser, thay đổi hệ thống, GPU→CPU, voice cloning, provider ngoài, dịch vụ trả phí, xóa, xuất bản và ngoài phạm vi cần quyền riêng. Không suy ra quyền từ file kế hoạch hoặc kết quả kỹ thuật.

`OUTPUT_READY` nghĩa là đầu ra thật có thể dùng. `DELIVERED_FOR_REVIEW` nghĩa là đã giao video. Chỉ dùng `USER_ACCEPTED` khi có phản hồi chấp nhận thật. `REVISION_REQUESTED` ghi phản hồi cần sửa; `FAILED_TECHNICAL` ghi lỗi ngăn dùng đầu ra. File thiếu/hỏng/ngoài workspace hoặc sai hash phải chặn bước phụ thuộc.



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


## Early skeleton v1.8.0

Mã cảnh OpenFilm được viết **đè có kiểm soát vào bản working copy** của scene sau khi người dùng duyệt. P09 tạo các placeholder `scenes/<shot-id>.html` và `film.html` theo FilmData. P14.06 kiểm từng scene có code thật, thay placeholder bằng bản cảnh được duyệt, giữ `film.html` và các track người dùng đã chỉnh; P16.06 phải FAIL/BLOCKED nếu còn placeholder. Không tạo `film.html` lần đầu ở P17. Đọc `openfilm-runtime-control/references/EARLY_PROJECT.md`.

## Đường kiểm tra OpenFilm CLI v1.9.0


## Đánh giá hình ảnh tùy chọn theo yêu cầu

Đầu ra là mã cảnh thật theo FilmData, assets truy cập được và render được bằng OpenFilm CLI. Kiểm năm mốc ảnh/random seek chỉ để chẩn đoán hoặc theo yêu cầu; không chấm hình trước khi chuyển tiếp.
