> v1.14.0: FINISH_FIRST_USER_REVIEW ưu tiên. Đây là công thức kỹ thuật/tham khảo; mọi đánh giá thẩm mỹ chỉ theo yêu cầu người dùng, mọi cổng QC legacy không chặn V01. OpenFilm CLI-first, GUI tùy chọn.

Chỉ dùng khi người dùng chủ động yêu cầu QC. Không có quyền chặn macro hoặc bàn giao.

# Quy trình đánh giá tùy chọn

Chỉ áp dụng khi người dùng yêu cầu đánh giá chất lượng. Không chặn sản xuất hoặc bàn giao V01. Các từ “bắt buộc” dưới đây chỉ ràng buộc báo cáo đánh giá được yêu cầu, không phải tiến độ phim.



# Nghiệm thu & render video

Không tuyên bố đã render chỉ vì đã viết mã nguồn. Đọc `openfilm-dinh-dang` và `openfilm-moi-truong` trước; chỉ dùng lệnh trên máy đã được người dùng cho phép.

## QC theo mỗi công việc

| Gate | Bằng chứng cần có | Đạt khi |
| --- | --- | --- |
| Cấu trúc | `film.html`, scene pages, relative assets | Không thiếu file/track sai |
| Kịch bản | shot list, lời thoại, timeline durations | Đủ shot và thứ tự |
| Hình | screenshots `openfilm look` ở đầu/giữa/cuối, và contact sheets | Không đen/trắng flash, clipping ngoài ý muốn |
| Chuyển động | so sánh cùng t được render hai lần | Deterministic, không giật hoặc lệch nhân vật |
| Audio | phát/nghe mẫu và đo `look --loudness` nếu runtime có | Voice rõ, âm thanh khớp, không clipping |
| Subtitle | .vtt cạnh audio/video và kiểm tra cue | Đúng câu và đồng bộ |
| Color | `openfilm color look` khi có runtime | Không cháy/tối bất thường, không jump màu |
| Xuất bản | file MP4 thực, metadata, xem lại | Đúng kích thước, thời lượng, âm thanh |

## Lệnh có trong tài liệu nguồn

- `openfilm look` tạo contact sheet và kiểm tra frame; `openfilm look 4.5` xem 1 giây; `openfilm look 3-6` xem khoảng thời gian; `openfilm look --full` soi toàn bộ file render; `openfilm look --loudness=-14` rà âm lượng.
- `openfilm render [a-b]` xuất MP4; tài liệu công bố các cờ `--4k`, `--blur`, `--alpha`. Chạy `openfilm render --help` phiên bản cài để xác định path, codec, fps, options trước khi render.
- Với phim chuẩn online, hướng dẫn gốc dùng loudness `-14 LUFS` trong render nếu không có yêu cầu khác. Không gán -14 như tiêu chuẩn bắt buộc cho mọi nền tảng.
- Render dở do crash có thể resume bằng cùng lệnh/option theo nguồn, nhưng chỉ kết luận resume nếu runtime xác minh thành công.

## Bàn giao

Bảng PASS/FAIL/BLOCKED theo từng gate, dẫn file/log/screenshot hiện có, câu lệnh dùng và phiên bản công cụ; liệt kê lỗi chưa sửa, không đánh đồng chưa kiểm tra với PASS. Nếu FAIL, đề xuất sửa tối thiểu và xin phê duyệt khi vượt phạm vi. Video kết quả chỉ là thành phẩm khi xác nhận MP4 tồn tại và phát được.

## Cổng nghiệm thu bổ sung khi có VieNeu-TTS

Nếu dự án dùng `openfilm-vieneu-tts`, bổ sung bảng `TTS-ENV`, `TTS-SCRIPT`, `TTS-WAV`, `TTS-LISTEN`, `TTS-SYNC`, `TTS-PUBLISH` từ `openfilm-vieneu-tts/references/INTEGRATION.md`. FFprobe kiểm chứng WAV thực, nghe duyệt âm thanh trước MP4, đối chiếu thời lượng và captions. Nếu không nghe được qua Remote Desktop Commander, xuất mẫu có thật để người dùng gửi lên chat; trạng thái `BLOCKED` cho phần nghe chưa nghiệm thu.

## QC master theo mode (v1.4)

Nếu `masterEngine=openfilm`: export MP4 từ OpenFilm đã có trên PC; nếu `masterEngine=remotion`: export từ Remotion đã có trên PC. Hai đường đều đọc `openfilm-render-profiles`, chạy `openfilm-qc-advanced` QC20, random frame, smoke 5 giây, codec/duration/audio bằng ffprobe và nghe bản cuối. Không tuyên bố đã render hoặc audio QC chỉ từ mã nguồn/JSON. `openfilm-sample-90s` là mẫu chưa có WAV/assets nên không được báo MP4 PASS.

## OpenFilm E2E 7 giây v1.8.0

P06.09–P06.11 chạy bộ thử **riêng** OpenFilm một cảnh có chuyển động, track WAV test-tone tự tạo tại workspace và WebVTT; yêu cầu `openProject`, `inspectFrame`, `renderClip` đã kiểm chứng, quyền chạy/render riêng. Dùng FFprobe kiểm MP4 thật + xem/chạy nghe; pass phải có e2e report, audio/visual review, bằng chứng. Chỉ audio test-tone nên **không** tính là nghe QC VieNeu; P12 và P18 vẫn độc lập. Xem `openfilm-smoke-e2e/SKILL.md`.

## Render bắt buộc OpenFilm CLI (v1.9.0)


## v1.12.0 — Mandatory Visual Inspection & Quality Gate
M5/M6/M7 bắt buộc trích và **truyền frame thật cho ChatGPT nhìn** từ đúng MP4 render tương ứng; `openfilm look`, exitCode và FFprobe KHÔNG thay thế trực tiếp kiểm frame. M4 image screenshot CLI cũng phải truyền vào model, không chỉ có đường dẫn. Nếu Remote Desktop Commander không trả image content, xuất PNG để user upload và BLOCKED. Không chấp nhận MP4 cuối khi Visual QC M7 thiếu hoặc ảnh hết hiệu lực. `openfilm-visual-inspection/SKILL.md` là nguồn nghiệm thu thị giác bắt buộc.
