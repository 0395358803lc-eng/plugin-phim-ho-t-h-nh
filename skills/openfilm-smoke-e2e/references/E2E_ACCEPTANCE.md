# Hợp đồng nghiệm thu E2E OpenFilm độc lập (P06.09–P06.11)

- Test video 7 giây có 1 trang cảnh `window.film.frame(t)` với vật thể di chuyển, `film.html` chứa track `<iframe>`, `<audio>` và `<track kind="captions">` + WebVTT; WAV 48kHz tạo tại chỗ không dùng TTS/service ngoài.
- Render bằng **OpenFilm** đã xác minh, không chấp nhận MP4 do Remotion hoặc FFmpeg trực tiếp để giả là OpenFilm.
- Đầu ra: MP4 thực trong `qc/openfilm-e2e/fixture/`, metadata JSON lấy từ FFprobe (không nhập tay), ảnh chụp nhiều mốc, log thực, xác nhận hình/tone/caption và báo cáo.
- `validate_e2e_report.py --workspace ... --report ...` kiểm trạng thái dữ liệu và file bằng chứng; phải đạt trước nghiệm thu P06.11. Bài test vẫn không thể tự nghe/nhìn chỉ từ JSON; người nghiệm thu phải xem-nghe thực. Báo PASS là về khả năng OpenFilm render HTML+WAV+VTT **trên máy đó**, không chứng minh chất lượng TTS, toàn phim, hoặc performance 4K.
- Phát hiện frame đen, không thấy vật thể thay đổi, mất tiếng, lỗi caption, sai duration/codec: FAIL + issue scoped, sửa sau phê duyệt; không tự bỏ bài test. Nếu GUI không thể tự điều khiển, báo giới hạn và hướng dẫn operator thao tác theo đường dẫn thật.

**Cold start:** `renderClip=UNVERIFIED` được phép ở đúng gói probe P06.10 sau khi xác minh binary/GUI method và được phê duyệt; chính MP4 + FFprobe + review P06.11 mới tạo chứng cứ `renderClip=VERIFIED` trong profile. Không buộc PASS trước phép thử đầu tiên.

**v1.9.0:** E2E PASS bắt buộc OpenFilm CLI; report gồm `executionMode=cli`, `cliRunEvidencePath` là record command real/exitCode=0; không thay bằng thao tác UI-only. `openfilm look/render` chạy trong fixture chứa film.html và chỉ sau phê duyệt.
