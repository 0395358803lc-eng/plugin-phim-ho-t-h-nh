---
name: openfilm-gsap
description: "Dùng khi xây dựng chuyển động nhân vật 2D, kinetic typography, camera pan/zoom và timeline tween bằng GSAP bên trong trang cảnh OpenFilm, với frame(t) tất định và phụ thuộc được kiểm kê trước."
---

Mặc định `FINISH_FIRST_USER_REVIEW`: hoàn thành video V01 rồi bàn giao để người dùng đánh giá. Chính sách này ưu tiên hơn hướng dẫn QC legacy. QC20, Visual QC và nghe chấm từng take chỉ chạy khi người dùng chủ động yêu cầu; không chặn sản xuất/bàn giao. Smoke và kiểm frame/random seek chỉ dùng để chẩn đoán lỗi kỹ thuật hoặc theo yêu cầu.

Giữ 8 macro M0–M7 và 99 ID packet. Một phê duyệt phạm vi rõ đầu vào, đầu ra, lệnh và quyền có thể bao phủ M1–M7. Không xin duyệt riêng từng packet/Pxx hoặc nghiệm thu từng macro. Chạy nhiều packet trong lượt High; ghi checkpoint sau mỗi đầu ra, tiếp tục cùng quyền trong lượt chat mới, không tự chạy nền.

OpenFilm CLI-first; Desktop/GUI chỉ để xem/chỉnh sửa tùy chọn. VieNeu-TTS GPU-first; cài đặt, tải model/browser, thay đổi hệ thống, GPU→CPU, voice cloning, provider ngoài, dịch vụ trả phí, xóa, xuất bản và ngoài phạm vi cần quyền riêng. Không suy ra quyền từ file kế hoạch hoặc kết quả kỹ thuật.

`OUTPUT_READY` nghĩa là đầu ra thật có thể dùng. `DELIVERED_FOR_REVIEW` nghĩa là đã giao video. Chỉ dùng `USER_ACCEPTED` khi có phản hồi chấp nhận thật. `REVISION_REQUESTED` ghi phản hồi cần sửa; `FAILED_TECHNICAL` ghi lỗi ngăn dùng đầu ra. File thiếu/hỏng/ngoài workspace hoặc sai hash phải chặn bước phụ thuộc.



# GSAP + OpenFilm · chuyển động 2D/timeline

## Điều kiện sử dụng

Sau cổng P00–P05 và phê duyệt dựng cảnh, xác minh `B01 GSAP` trong `VIDEO_HOAT_HINH_WORKSPACE`/workspace cũ/app hay dự án đã có. Không chạy `npm install`/sử dụng CDN online khi chưa được duyệt. Library GSAP phải truy cập được từ **cảnh HTML cụ thể** bằng đường dẫn vendor/import map/bundler được kiểm chứng. Không khẳng định GSAP đã tích hợp chỉ vì tìm thấy một thư mục package.

## Thiết kế frame-driven

- Timeline GSAP **dừng ngay từ đầu**: `gsap.timeline({paused:true})`; nếu chuyển động có nhiều diễn biến, tổ chức labels/keyframes/eases minh bạch.
- `window.film.frame(t)` sẽ `.pause().seek(t, true)` để nhảy playhead theo giây (suppress events) và hoàn tất render; không `.play()` hoặc phụ thuộc real time khi có `window.filmHost`.
- Không sử dụng callbacks gây hiệu ứng không thể tua lại, audio tự bật, Tween lặp vô hạn, random không seed, hoặc state phụ thuộc thứ tự gọi. Khi có GSAP + WebGL, seek GSAP xong gọi Three.js renderer trong cùng frame.
- Trạng thái đầu/đích cần ổn định ở t=0 và t=duration. Thử các thứ tự `0 -> 2 -> 0.5 -> 2 -> 0` để phát hiện bất định. Tránh layout thrash và plugin GSAP trả phí/khác giấy phép chưa được xác minh.

## Output / QC

Cảnh `scenes/*.html` điều khiển bằng `frame(t)`; sample: `references/gsap-scene.html` (đường dẫn JS là ví dụ, phải thay bằng nguồn B01 thực). QC font loading, phân lớp, vùng an toàn 9:16/16:9, easing mượt, chuyển động không giật ở cut. Khi GSAP không cần thiết thì dùng CSS/JS cơ bản của OpenFilm, không thêm dependency.

Nguồn kỹ thuật GSAP: https://gsap.com/docs/v3/GSAP/Timeline/seek%28%29/ .

## GSAP khi chọn Remotion Master (N08)

Cùng nguyên tắc paused + seek nhưng timeline gốc là frame Remotion: `const frame=useCurrentFrame(); const {fps}=useVideoConfig(); tl.seek(frame/fps)` khi DOM đã mount và các tween `fromTo` có start/end xác định. Với hiệu ứng đơn giản ưu tiên `interpolate` để tránh effect/state của GSAP gây lệch frame trong SSR. Không để timeline tự play/ticker; không truy cập `window` ở module scope khi SSR. Xem `openfilm-audio-subtitles` để xử lý phần audio nằm ngoài scene GSAP.

## Đánh giá hình ảnh tùy chọn theo yêu cầu
