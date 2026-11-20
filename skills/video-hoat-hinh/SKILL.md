---
name: video-hoat-hinh
description: "Điều phối sản xuất hoạt hình V01 hoàn chỉnh trước khi người dùng đánh giá."
---

# video-hoat-hinh — v1.14.0

Mặc định `FINISH_FIRST_USER_REVIEW`: hoàn thành video V01 rồi bàn giao để người dùng đánh giá. Chính sách này ưu tiên hơn hướng dẫn QC legacy. QC20, Visual QC và nghe chấm từng take chỉ chạy khi người dùng chủ động yêu cầu; không chặn sản xuất/bàn giao. Smoke và kiểm frame/random seek chỉ dùng để chẩn đoán lỗi kỹ thuật hoặc theo yêu cầu.

Giữ 8 macro M0–M7 và 99 ID packet. Một phê duyệt phạm vi rõ đầu vào, đầu ra, lệnh và quyền có thể bao phủ M1–M7. Không xin duyệt riêng từng packet/Pxx hoặc nghiệm thu từng macro. Chạy nhiều packet trong lượt High; ghi checkpoint sau mỗi đầu ra, tiếp tục cùng quyền trong lượt chat mới, không tự chạy nền.

OpenFilm CLI-first; Desktop/GUI chỉ để xem/chỉnh sửa tùy chọn. VieNeu-TTS GPU-first; cài đặt, tải model/browser, thay đổi hệ thống, GPU→CPU, voice cloning, provider ngoài, dịch vụ trả phí, xóa, xuất bản và ngoài phạm vi cần quyền riêng. Không suy ra quyền từ file kế hoạch hoặc kết quả kỹ thuật.

`OUTPUT_READY` nghĩa là đầu ra thật có thể dùng. `DELIVERED_FOR_REVIEW` nghĩa là đã giao video. Chỉ dùng `USER_ACCEPTED` khi có phản hồi chấp nhận thật. `REVISION_REQUESTED` ghi phản hồi cần sửa; `FAILED_TECHNICAL` ghi lỗi ngăn dùng đầu ra. File thiếu/hỏng/ngoài workspace hoặc sai hash phải chặn bước phụ thuộc.

| Macro | Giai đoạn | Đầu ra và điều kiện tiếp tục |
|---|---|---|
| M0 | P00–P06 | Chọn máy/workspace, tái dùng runtime, phê duyệt thao tác đặc biệt. Fixture 7 giây chỉ dùng lần kiểm chứng runtime đầu hoặc chẩn đoán. |
| M1 | P07–P09 | Đọc đủ 7 tệp, chốt thông số trong phạm vi đã duyệt, tạo FilmData và film.html. |
| M2 | P10–P11 | Storyboard, nhân vật, bối cảnh, asset thật; ZIP và xác minh file sau giải nén. |
| M3 | P12–P13 | WAV VieNeu GPU, thời lượng thực, phụ đề. Bỏ qua có lý do nếu phim không có thoại. |
| M4 | P14–P16 | Mã cảnh 2D/3D theo FilmData, đủ tài sản và không còn placeholder cản render. |
| M5 | P17–P18 | Timeline hoàn chỉnh. P18 smoke chỉ khi chẩn đoán hoặc user yêu cầu. |
| M6 | P19–P20 | Render toàn phim thành V01.mp4, giải mã và kiểm stream. P20 chỉ kích hoạt sau phản hồi người dùng, không chặn P21. |
| M7 | P21 | Bàn giao trực tiếp V01 nếu đúng định dạng, source/WAV/phụ đề/manifest. Không render lại master trùng nội dung; không tự xuất bản. |

Đọc [openfilm-macro-bundles](../openfilm-macro-bundles/SKILL.md) và [quy trình](../openfilm-production-p06-p21/SKILL.md).


Đường thực thi `CLI_ONLY_FOR_OPENFILM`: đọc [openfilm-cli-execution](../openfilm-cli-execution/SKILL.md).

P00–P05: chọn máy/workspace, kiểm tra công cụ hiện có và quyền cài đặt trước sản xuất.
