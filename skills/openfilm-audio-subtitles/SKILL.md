---
name: openfilm-audio-subtitles
description: "Đồng bộ thoại WAV VieNeu-TTS, caption tiếng Việt SRT/VTT, nhạc nền ducking và QC âm thanh cho cả OpenFilm/Remotion Master." 
---

# Âm thanh, phụ đề Việt và ducking frame-based (N10–N12)

Bắt đầu từ `openfilm-vieneu-tts`: manifest theo shot/character/voice, chuẩn hóa phát âm (giữ `script_original`), model đã được người dùng duyệt. Audio phải có **file WAV có thật**, đo `ffprobe` sample rate/duration/channels và nghe QC. Nếu remote không truyền âm thanh, xuất mẫu có thể tải để người dùng cung cấp; không giả đã nghe. Không tự clone giọng người thật chưa được phép.

## Căn thời lượng

1. Tạo từng `s02_l01.wav` theo thoại, không ghi đè bản duyệt; dùng path relative, ghi revision model/backend.
2. Sau khi WAV ra file, đo duration thực; `endFrame = startFrame + ceil(duration_s * fps)` (đối chiếu silences/fades); so với shot boundary, nếu vượt cảnh, **báo và yêu cầu chọn** mở rộng shot, sửa kịch bản/tốc độ đọc hợp lệ, hoặc dời lời thoại; không tự cắt nội dung đã duyệt.
3. `subtitle` sentence timing chỉ là dự thảo khi có onset/duration toàn câu; **word-level sync** cần alignment/căn bằng tai thật. Không tạo timecode từ số ký tự. Đặt audio master duy nhất để không phát lặp khi OpenFilm/Remotion bridge.
4. SRT dùng `HH:MM:SS,mmm`, WebVTT dùng `HH:MM:SS.mmm`. Chuyển từ integer frame giữ đúng FPS; cue start < end, không đi ra ngoài duration, tránh chồng khi không có 2 speaker đồng thời.
5. Chọn font tiếng Việt chứa glyph `ă â ê ô ơ ư đ` và dấu thanh; đặt trong project nếu cần tái lập; kiểm tra bằng render tại nhiều khung hình và safe area 16:9/9:16.

## Mix và ducking

- OpenFilm Master: giữ voice/music/SFX trên các track `<audio>` riêng trong `film.html`, đừng phát từ trang cảnh. Remotion Master: `<Sequence>` và `<Audio src={staticFile(...)} volume={frame=>...} />` với timeline `film.json` (không dùng thời gian thực).
- Khi `frame` thuộc `[startFrame,endFrame)` của một câu thoại, giảm nhạc nền theo curve mềm (attack/release do dự án chốt), tránh nhảy volume giữa các frame. Bắt đầu bằng giá trị thử nghiệm, rồi nghe/QC; không khẳng định hệ số 0.07/0.18 là tiêu chuẩn loudness.
- `ffmpeg ebur128` để đo loudness, đo peak/clipping, nghe nhạc nền có che lời nói không; mục tiêu theo nền tảng do người dùng yêu cầu, không mặc định -14 LUFS cho mọi video.
- Thử file bị thiếu/không đọc được/sai tần số; báo FAIL/BLOCKED và giữ master chưa xuất. Quyền âm nhạc, SFX phải đủ.

Mẫu logic và quy tắc xuất SRT trong `references/AUDIO_CAPTIONS.md`. Kết quả gồm WAV manifest, cue SRT/VTT, ffprobe report, bảng QC nghe và cờ `SYNC_PASS` chỉ sau chứng cứ.
