> v1.14.0: FINISH_FIRST_USER_REVIEW ưu tiên. Đây là công thức kỹ thuật/tham khảo; mọi đánh giá thẩm mỹ chỉ theo yêu cầu người dùng, mọi cổng QC legacy không chặn V01. OpenFilm CLI-first, GUI tùy chọn.

Chỉ dùng khi người dùng chủ động yêu cầu QC. Không có quyền chặn macro hoặc bàn giao.

# Quy trình đánh giá tùy chọn

Chỉ áp dụng khi người dùng yêu cầu đánh giá chất lượng. Không chặn sản xuất hoặc bàn giao V01. Các từ “bắt buộc” dưới đây chỉ ràng buộc báo cáo đánh giá được yêu cầu, không phải tiến độ phim.



# OpenFilm mandatory visual inspection — v1.12.0


## Đầu vào và cổng nhìn thực

1. Xác minh đúng máy Windows `deviceId` và `WORKSPACE` đã được duyệt. Trong từng macro, chọn đầu ra **đã tạo thật**, kiểm `SHA256`, đường dẫn, render version/revision, shot/asset manifest. Các cảnh 2D/3D: `openfilm look` **CLI**; các video smoke/draft/master: trích **từ MP4 vừa render bằng FFmpeg** (không dùng screenshot của HTML hay storyboard để thay ảnh frame từ MP4). CLI dùng executable/cwd đã được P06 nghiệm thu và lệnh trong scope macro; không `npx @latest`, không tải/cài không duyệt.
2. Chuẩn hóa ảnh làm PNG theo target resolution hoặc preview đủ rõ. M2 render SVG/PDF/HTML storyboard/asset thành **ảnh viewable** trên máy theo công cụ sẵn có đã duyệt; không xem text SVG thay ảnh. M4 mỗi shot bắt buộc 5 mốc START/Q1/MID/Q3/END + shot-boundary, random seek và chuỗi bổ sung khi cần. M5 một video smoke 5 giây với 5 mốc. M6 và M7 trích START/MID/END cho **mọi shot** từ đúng file draft/master MP4; thêm cut boundaries và đoạn hành động nhanh theo rủi ro; không lấy 3 ảnh đại diện rồi tuyên bố đã xem toàn phim.
3. Dùng công cụ **Remote Desktop Commander** `read_file` với PNG/JPEG/WebP hoặc `read_multiple_files` với **đường dẫn thật** và đúng `deviceId/link_id`; kiểm tra kết quả trả về là **các hình ảnh thực mà mô hình nhìn được** (image content/multimodal, không chỉ base64 text hay `success=true`). Khi gọi qua `functions.exec`, chuyển từng image-part nhận được ra đầu ra mô hình bằng `image(part)` nếu cần. Nếu connector không truyền ảnh vào model, xuất ảnh để người dùng tải/gửi lên chat; chặn `VISUAL_BLOCKED`, không ghi receipt giả, không kết luận đã nhìn.
4. **Sau khi trực tiếp nhìn từng ảnh**, ghi cho mỗi target và mốc: `imagePath`, `imageSha256`, `sourceSha256`, `transferMethod`, `hostImageEvidence` từ phản hồi công cụ thực (nếu phản hồi không có ref riêng, dùng mã phiên đọc thực đã xác minh), `imageActuallyReceived=true`, nhận xét riêng về nội dung đang thấy (`observation`), `assessment=PASS/FAIL/BLOCKED`, `issues[]`. Đừng dùng nhận xét chung `OK`/`file exists`; không sinh ghi chú từ metadata. Kiểm cấu trúc cảnh, tỷ lệ, ánh sáng, màu, tay/mặt, typography tiếng Việt, texture, crop, continuity và sai khác với storyboard thực.
5. Khi FAIL: tạo issue với screenshot, frame/shot, nguyên nhân, scope fix, kiểm quyền theo macro; sửa chỉ phần đã duyệt rồi dựng lại ảnh/video **và đọc lại hình mới**. Hash/revision đổi → invalidate report/các target bị ảnh hưởng; không dùng ảnh cũ để PASS render mới. Dừng nếu thiếu quyền sửa lớn hay cần quyết định phong cách. Không tự đổi style/nguồn asset/trả phí trong macro thường.
6. Lưu `qc/visual/Mx/VISUAL_QC_REPORT.json` và bằng chứng PNG/command log `qc/visual/Mx/`. Đối chiếu `reports/WORK_UNIT_INDEX.json.visualTargets[Mx]` với IDs thật từ storyboard/FilmData đã xác minh; thiếu 1 target hoặc mốc bắt buộc → `VISUAL_BLOCKED`. Chạy `validate_visual_qc.py REPORT --workspace WORKSPACE --targets-json verified-targets.json` trên máy **được phép** để đối chiếu bytes/hash/provenance; script KHÔNG thể chứng minh mô hình đã nhận pixel hay chất lượng thẩm mỹ thật. Đây là hai phép kiểm riêng; **cả hai đều cần**.

## Chất lượng nhìn theo nhóm

- **M2 P10/P11**: nhìn ảnh storyboard từng shot, mẫu nhân vật chính, bối cảnh và asset quan trọng, so style bible và continuity. `visualTargets[M2]` phải gồm các ID storyboard, nhân vật/bối cảnh được duyệt — tạo từ manifest thực, không lấy ví dụ hay tự rút gọn.
- **M4 P14–P16**: nhìn frame **OpenFilm CLI look** thật tại nhiều vị trí, so hoạt ảnh liên tiếp, camera cut, layer, răng cưa, texture, vùng an toàn, typography, biểu cảm. Một contact sheet cần đủ rõ từng panel và nhận xét từng mốc; nếu thiếu độ phân giải thì đọc ảnh crop/full-size riêng.
- **M5 P17–P18**: trích 5 mốc từ MP4 smoke vừa render; so scene với storyboard và kiểm hình, phụ đề hiện trên ảnh. FFprobe + kiểm âm thanh riêng; ảnh không chứng minh đã nghe.
- **M6 P19–P20**: frame trích từ **draft MP4** tại mỗi shot + sát cut; QC20 hình ảnh toàn phim dựa trên ảnh quan sát thực, không chỉ text report.
- **M7 P21**: trích lại từ **FINAL_MASTER.mp4** (khác draft), kiểm từng shot, đầu/cuối/cut và tính nhất quán. Báo rõ chỉ kiểm frame mẫu, **không tuyên bố đã xem liên tục toàn bộ phim** nếu chưa thực sự xem video. Nghiệm thu âm thanh và người dùng vẫn độc lập.

## Mô hình bằng chứng/giới hạn trung thực

`validate_visual_qc.py` kiểm path an toàn, nguồn MP4 thật, frame PNG, hash và mẫu bắt buộc, chi tiết receipt. Nó không phải mô hình thị giác và **không thể kiểm chứng bằng mật mã rằng ChatGPT đã thật sự nhìn ảnh**. Đừng tạo `imageActuallyReceived=true`, `hostImageEvidence` hoặc nhận xét khi công cụ trả về chỉ log, tên file hay base64 text mà ảnh chưa hiện trong đầu vào thị giác. Trường hợp đó là `VISUAL_BLOCKED`; xuất file ảnh để người dùng gửi vào chat hoặc dùng con đường hình ảnh có thật khác. Không hứa một lệnh máy sẽ tự xác nhận đẹp nhất; đánh giá thẩm mỹ phải so phong cách đã duyệt và có thể đề xuất cải tiến.

**Tài liệu:** `references/VISUAL_QC_POLICY.json`, `references/VISUAL_QC_REPORT_TEMPLATE.json`, `references/FRAME_SAMPLING.md`, `references/validate_visual_qc.py`, `references/sample_render_frames.py`.
