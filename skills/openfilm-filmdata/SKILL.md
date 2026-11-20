---
name: openfilm-filmdata
description: "Chuẩn hóa FilmData, shot/audio/timeline frame, asset manifest và kiểm tra dữ liệu giữa OpenFilm, GSAP, Three.js, Remotion, VieNeu-TTS." 
---

Mặc định `FINISH_FIRST_USER_REVIEW`: hoàn thành video V01 rồi bàn giao để người dùng đánh giá. Chính sách này ưu tiên hơn hướng dẫn QC legacy. QC20, Visual QC và nghe chấm từng take chỉ chạy khi người dùng chủ động yêu cầu; không chặn sản xuất/bàn giao. Smoke và kiểm frame/random seek chỉ dùng để chẩn đoán lỗi kỹ thuật hoặc theo yêu cầu.

Giữ 8 macro M0–M7 và 99 ID packet. Một phê duyệt phạm vi rõ đầu vào, đầu ra, lệnh và quyền có thể bao phủ M1–M7. Không xin duyệt riêng từng packet/Pxx hoặc nghiệm thu từng macro. Chạy nhiều packet trong lượt High; ghi checkpoint sau mỗi đầu ra, tiếp tục cùng quyền trong lượt chat mới, không tự chạy nền.

OpenFilm CLI-first; Desktop/GUI chỉ để xem/chỉnh sửa tùy chọn. VieNeu-TTS GPU-first; cài đặt, tải model/browser, thay đổi hệ thống, GPU→CPU, voice cloning, provider ngoài, dịch vụ trả phí, xóa, xuất bản và ngoài phạm vi cần quyền riêng. Không suy ra quyền từ file kế hoạch hoặc kết quả kỹ thuật.

`OUTPUT_READY` nghĩa là đầu ra thật có thể dùng. `DELIVERED_FOR_REVIEW` nghĩa là đã giao video. Chỉ dùng `USER_ACCEPTED` khi có phản hồi chấp nhận thật. `REVISION_REQUESTED` ghi phản hồi cần sửa; `FAILED_TECHNICAL` ghi lỗi ngăn dùng đầu ra. File thiếu/hỏng/ngoài workspace hoặc sai hash phải chặn bước phụ thuộc.



# FilmData + timeline duy nhất + asset provenance (N03–N05)

Đọc `openfilm-hybrid-master` trước. `film.json` ở `projects/<film-id>/scene-data/film.json` là **nguồn dữ liệu hợp đồng**, không phải định dạng mà OpenFilm tự sinh. Khi bắt đầu mới, tạo `schemaVersion=1`, `filmId`, `masterEngine` (`openfilm` hoặc `remotion`), `fps`, `width`, `height`, `durationInFrames`, `shots[]`, `dialogues[]`; template và kiểm tra trong `references/`.

## Thời gian và phát hiện sai lệch

- `startFrame` bắt đầu 0; `durationInFrames` là số nguyên dương; khoảng **half-open** `[start, start+duration)`. `endFrame` của dialogue là giới hạn *không bao gồm* frame cuối.
- `t_seconds = frame / fps`; `frame = round(t_seconds*fps)` chỉ ở **biên chuyển đổi** (cần quy tắc rounding thống nhất). Lưu thời gian master dưới số nguyên frame, không cộng số thực từng lần.
- Dòng thoại trỏ đúng `shotId`, start/end nằm trong shot. Mỗi shot có stable ID; không cắt chồng/gap khi không có chủ ý rõ. Audio thực do VieNeu sinh được đo FFprobe, chỉ sau đó mới cập nhật endFrame (và các shot bị ảnh hưởng phải được người dựng xét duyệt). Nếu chưa có audio thì `PENDING_AUDIO`, không được đánh dấu SYNC PASS.
- Nhân vật/voice, scene loại 2D/3D và nguồn asset phải giữ tính nhất quán; hash của file **thực** và giấy phép khi có bằng chứng.

## Lưu trữ và công cụ

- Schema: `references/film-data.schema.json`; ví dụ 90s: `openfilm-sample-90s/references/film.json`.
- `references/validate_filmdata.py` là **script Python stdlib, chỉ đọc**: kiểm tra cấu trúc, frame, shot, ID, path an toàn. Khi dùng `--check-assets <project-root>` còn kiểm sự tồn tại của WAV/asset. Không tuyên bố JSON đã có WAV nếu chưa chạy tạo giọng.
- Asset manifest riêng mô tả license/creator/sha256 nếu đã có thực, trạng thái `MISSING`/`VERIFIED`/`PENDING`; không đưa secret/key/cookie vào manifest. Hash chỉ được ghi khi tính từ file thật.
- Khi tái sử dụng `node_modules` từ workspace cũ, lock/ABI/platform và resolver phải đúng; khi không phù hợp xin duyệt cài cục bộ theo P05.

QC tối thiểu: validate JSON; 6 shot sample liên tục đủ 2700 frames; 7 dialogue nằm trong shot, file WAV sample chưa có => check-assets FAIL có chủ ý. Chỉ dùng `openfilm-qc-advanced` khi user yêu cầu.

## P07–P09 theo bộ 7 tệp kịch bản

Trước P09, P07 phải đọc nội dung thật theo `openfilm-script-input`, xác minh header CSV và mapping scene/dialogue/person vào FilmData, giữ source bản gốc. Không lấy ảnh danh sách tệp thay cho nội dung. P09 cung cấp FilmData đã kiểm chứng cho checkpoint `openfilm-checkpoint-approval`; khi WAV thật thay thời lượng thì invalidation P13 và những scene/timeline downstream bị ảnh hưởng sau duyệt.

## Đánh giá hình ảnh tùy chọn theo yêu cầu
