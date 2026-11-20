---
name: openfilm-smoke-e2e
description: "Kiểm thử độc lập OpenFilm trên Windows trước phim dài với fixture 7 giây có HTML chuyển động, WAV tone 48kHz, phụ đề VTT; render MP4, FFprobe và xem/nghe có bằng chứng."
---

# OpenFilm end-to-end smoke 7s (v1.8.0)

**Không đánh đồng fixture với phim hoàn chỉnh, và tuyệt đối không coi có code HTML là video PASS.** P06.09/10/11 chạy sau runtime profile, phê duyệt ghi/render, và phải dùng đúng OpenFilm runtime đã xác minh. Đây là bài thử *độc lập* trước khi xử lý phim dài; P18 là smoke của phim thật, vẫn bắt buộc.

## Packet P06.09 — chuẩn bị fixture (ghi sau approval)

Đọc `openfilm-runtime-control` và `OPENFILM_RUNTIME_PROFILE.json`, xác nhận đường dẫn workspace. `references/create_e2e_fixture.py --workspace <WORKSPACE> --create` tạo **chỉ trong** `qc/openfilm-e2e/fixture/`:

- `film.html` với một iframe tới `scenes/probe.html` dài 7s, **chuyển động thay đổi theo `window.film.frame(t)`**.
- `audio/probe-tone.wav`: tín hiệu âm gốc tạo bằng Python stdlib `wave`, PCM 48kHz, 2,5s — giúp xác minh tuyến âm thanh OpenFilm, **không** phải sản phẩm VieNeu và không thể xác minh chất lượng giọng nói.
- `captions/probe.vtt`: WebVTT chứa cue 1.0–3.5s. Media cục bộ/tương đối; không CDN/provider/model download.

Nếu file đã tồn tại, không ghi đè, kiểm nội dung và xem như `EXISTING/NEEDS_RECONCILE`. Không cài gì, không chạy render khi chỉ tạo fixture. Tập lệnh mặc định là preview/plan khi không có `--create`.

## Packet P06.10 — render OpenFilm thật

- Chỉ sau phê duyệt **render** cho fixture, chọn **CLI đã xác minh đường dẫn/lệnh** hoặc **Desktop UI đã thực sự điều khiển được**. Xác định lệnh/đích output và cờ theo `--help` bản cài; không giả định `openfilm render` có tham số cụ thể và không dùng `npx` có thể tải ngầm.
- **Cold-start probe:** nếu `renderClip=UNVERIFIED` (máy chưa từng được test), cho phép đúng một lần render fixture sau khi đã xác minh binary/command hoặc đường thao tác GUI và user duyệt gói `P06.10`. Đây là phép thử để *tạo evidence*; sau P06.11 PASS mới được đặt `renderClip=VERIFIED`. Nếu OpenFilm executable không thể định danh, GUI không điều khiển được, hoặc chưa có approval thì BLOCKED. Không yêu cầu renderClip PASS *trước* lần render kiểm chứng đầu tiên.
- Chạy trong fixture dir bằng phương thức đã duyệt, lưu MP4 đúng output thực và stdout/stderr/log có bằng chứng. Bản mục tiêu 7s; không tự tuyên bố codec/fps khi chưa đo.
- Nếu UI-only và không thể tự thao tác, yêu cầu user xuất qua giao diện, chờ file được tạo tại vị trí đã duyệt; trạng thái `BLOCKED/WAITING_FOR_USER`.

## Packet P06.11 — nghiệm thu có chứng cứ

- Xác minh MP4 có kích thước dương, FFprobe từ binary tin cậy (A04) ghi JSON thật với audio+video, duration khoảng 7s (dung sai theo frame/codec), resolution/fps từ profile; không dùng chữ trên log làm bằng chứng file hợp lệ.
- Kiểm hình ở đầu/giữa/cuối (di chuyển xảy ra), phụ đề VTT xuất hiện đúng và âm tone thực sự nghe được. Lưu `qc/openfilm-e2e/E2E_REPORT.json` có field status/metadata/paths/visualReview/audioReview/reviewer approval, **không tự điền PASS**. Đọc `references/E2E_ACCEPTANCE.md` và `validate_e2e_report.py` (validator metadata/evidence, không tự nghe).
- Thiếu replay kiểm chứng hình/tiếng, FFprobe hoặc output => `NOT_TESTED/BLOCKED`, không mở P07 nếu E2E bắt buộc và không có ngoại lệ phạm vi được duyệt. Không thay bằng clip Remotion hoặc bằng WAV tạo ra mà chưa import/render qua OpenFilm.

Fixture dùng tiếng tone, không động đến nguồn VieNeu và không được coi là GPU-TTS PASS. GPU smoke WAV riêng P06.06 và thoại thật P12 vẫn giữ nguyên.

## Bắt buộc CLI v1.9.0

Trước P06.10 kiểm `OPENFILM_RUNTIME_PROFILE.json.mode=cli`, CLI entrypoint tuyệt đối và cwd=`qc/openfilm-e2e/fixture` dưới workspace. Dùng `openfilm look` sau duyệt (tạo PNG) và `openfilm render --out` theo help bản thực (tạo MP4). Mọi thao tác có `CLI_RUN` và exitCode/log evidence; P06.11 chỉ PASS sau FFprobe/visual/audio/caption review. `E2E_REPORT` phải ghi `executionMode=cli` và `cliRunEvidencePath`; không chấp nhận GUI/Remotion/FFmpeg tạo clip thay OpenFilm CLI.
