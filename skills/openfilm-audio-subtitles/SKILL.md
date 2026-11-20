---
name: openfilm-audio-subtitles
description: "Đồng bộ thoại WAV VieNeu-TTS, caption tiếng Việt SRT/VTT, nhạc nền ducking và QC âm thanh cho cả OpenFilm/Remotion Master." 
---

Mặc định `FINISH_FIRST_USER_REVIEW`: hoàn thành video V01 rồi bàn giao để người dùng đánh giá. Chính sách này ưu tiên hơn hướng dẫn QC legacy. QC20, Visual QC và nghe chấm từng take chỉ chạy khi người dùng chủ động yêu cầu; không chặn sản xuất/bàn giao. Smoke và kiểm frame/random seek chỉ dùng để chẩn đoán lỗi kỹ thuật hoặc theo yêu cầu.

Giữ 8 macro M0–M7 và 99 ID packet. Một phê duyệt phạm vi rõ đầu vào, đầu ra, lệnh và quyền có thể bao phủ M1–M7. Không xin duyệt riêng từng packet/Pxx hoặc nghiệm thu từng macro. Chạy nhiều packet trong lượt High; ghi checkpoint sau mỗi đầu ra, tiếp tục cùng quyền trong lượt chat mới, không tự chạy nền.

OpenFilm CLI-first; Desktop/GUI chỉ để xem/chỉnh sửa tùy chọn. VieNeu-TTS GPU-first; cài đặt, tải model/browser, thay đổi hệ thống, GPU→CPU, voice cloning, provider ngoài, dịch vụ trả phí, xóa, xuất bản và ngoài phạm vi cần quyền riêng. Không suy ra quyền từ file kế hoạch hoặc kết quả kỹ thuật.

`OUTPUT_READY` nghĩa là đầu ra thật có thể dùng. `DELIVERED_FOR_REVIEW` nghĩa là đã giao video. Chỉ dùng `USER_ACCEPTED` khi có phản hồi chấp nhận thật. `REVISION_REQUESTED` ghi phản hồi cần sửa; `FAILED_TECHNICAL` ghi lỗi ngăn dùng đầu ra. File thiếu/hỏng/ngoài workspace hoặc sai hash phải chặn bước phụ thuộc.



# Âm thanh, phụ đề Việt và ducking frame-based (N10–N12)

Bắt đầu từ `openfilm-vieneu-tts`: manifest theo shot/character/voice, chuẩn hóa phát âm (giữ `script_original`), model đã được người dùng duyệt. Audio phải có **file WAV có thật**, đo `ffprobe` sample rate/duration/channels và kiểm giải mã. Người dùng đánh giá giọng trong V01; không giả đã nghe. Không tự clone giọng người thật chưa được phép.

## Căn thời lượng

1. Tạo từng `s02_l01.wav` theo thoại, không ghi đè bản duyệt; dùng path relative, ghi revision model/backend.
2. Sau khi WAV ra file, đo duration thực; `endFrame = startFrame + ceil(duration_s * fps)` (đối chiếu silences/fades); so với shot boundary, nếu vượt cảnh, **báo và yêu cầu chọn** mở rộng shot, sửa kịch bản/tốc độ đọc hợp lệ, hoặc dời lời thoại; không tự cắt nội dung đã duyệt.
3. `subtitle` sentence timing chỉ là dự thảo khi có onset/duration toàn câu; **word-level sync** cần alignment/căn bằng tai thật. Không tạo timecode từ số ký tự. Đặt audio master duy nhất để không phát lặp khi OpenFilm/Remotion bridge.
4. SRT dùng `HH:MM:SS,mmm`, WebVTT dùng `HH:MM:SS.mmm`. Chuyển từ integer frame giữ đúng FPS; cue start < end, không đi ra ngoài duration, tránh chồng khi không có 2 speaker đồng thời.
5. Chọn font tiếng Việt chứa glyph `ă â ê ô ơ ư đ` và dấu thanh; đặt trong project nếu cần tái lập; kiểm tra bằng render tại nhiều khung hình và safe area 16:9/9:16.

## Mix và ducking

- OpenFilm Master: giữ voice/music/SFX trên các track `<audio>` riêng trong `film.html`, đừng phát từ trang cảnh. Remotion Master: `<Sequence>` và `<Audio src={staticFile(...)} volume={frame=>...} />` với timeline `film.json` (không dùng thời gian thực).
- Khi `frame` thuộc `[startFrame,endFrame)` của một câu thoại, giảm nhạc nền theo curve mềm (attack/release do dự án chốt), tránh nhảy volume giữa các frame. Bắt đầu bằng cấu hình dự án; nghe đánh giá khi user yêu cầu; không khẳng định hệ số 0.07/0.18 là tiêu chuẩn loudness.
- `ffmpeg ebur128` để đo loudness, đo peak/clipping, nghe nhạc nền có che lời nói không; mục tiêu theo nền tảng do người dùng yêu cầu, không mặc định -14 LUFS cho mọi video.
- Thử file bị thiếu/không đọc được/sai tần số; báo FAIL/BLOCKED và giữ master chưa xuất. Quyền âm nhạc, SFX phải đủ.

Mẫu logic và quy tắc xuất SRT trong `references/AUDIO_CAPTIONS.md`. Kết quả gồm WAV manifest, cue SRT/VTT, ffprobe report, manifest thời lượng thực và trạng thái OUTPUT_READY.
