# QC nâng cao tùy chọn — v1.14.1

Chỉ kích hoạt khi user yêu cầu QC chuyên sâu hoặc một phép chẩn đoán kỹ thuật cụ thể. Không tự chạy QC20, smoke, random seek ở mọi lần render. Bộ kiểm tra này không cấp quyền, không đổi video thành USER_ACCEPTED và không chặn V01 chỉ vì báo cáo chưa có.

## Determinism và random seek

FilmData dùng integer frames, random có seed. GSAP paused+seek, Three/R3F transform tính từ thời gian/frame; audio trên track riêng. Khi cần chẩn đoán, so cùng frame sau thứ tự khác nhau, ví dụ [0,90,15,90,0] nếu clip đủ dài. Dùng t=frame/fps cho OpenFilm hoặc useCurrentFrame cho Remotion. Lưu ảnh source/version và môi trường GPU; so pixel trong tolerance phù hợp, không đòi bit-identical giữa GPU khác.

Kiểm boundary endFrame-1/next.startFrame để tìm flash, thiếu media hoặc jump. Chỉ thử phần có liên quan lỗi; sau sửa giữ bằng chứng trước/sau, không mở vòng nghiệm thu toàn bộ phim.

## Smoke có mục đích

Khi cần, render một đoạn đại diện 5 giây (5×fps frames) bằng runtime hiện có: hình, WAV, subtitle, 3D nếu phim có. P06 tone fixture kiểm đường render/audio; nó không chứng minh VieNeu hoạt động. P18 sample phim thật chỉ dùng để chẩn đoán tích hợp khi cần; không có quy tắc P18 FAIL khóa P19 do thiếu đánh giá thẩm mỹ.

Ghi command, output, decode/probe và phần đã xem/nghe thực tế. Lỗi kỹ thuật xác định được phải sửa trong scope trước khi dùng file hỏng; thiếu yêu cầu QC thì không tạo nghĩa vụ nghe/xem thêm.

## QC20 khi được yêu cầu rõ

Danh mục tham khảo ở [QC20.md](QC20.md). Ghi trạng thái từng mục PASS/FAIL/NOT_VERIFIED và bằng chứng; mục không phù hợp có lý do. Tập trung source/script, asset/license, font, framing, determinism, voice/captions, color, encode và package. Không phục hồi quy tắc khóa P19/P21, phê duyệt từng stage hoặc bắt user nghe mỗi take từ tài liệu cũ.

Báo cáo chỉ kết luận trong phạm vi thực kiểm. Review bản V01 không áp cho V02 khi hash đổi. Đề nghị sửa có targetIds và category rõ; execution dùng quyền hiện hành, chỉ xin quyền mới cho phần ngoài scope. Bàn giao phim vẫn theo finish-first và đánh giá cuối của người dùng.
