> v1.14.0: FINISH_FIRST_USER_REVIEW ưu tiên. Đây là công thức kỹ thuật/tham khảo; mọi đánh giá thẩm mỹ chỉ theo yêu cầu người dùng, mọi cổng QC legacy không chặn V01. OpenFilm CLI-first, GUI tùy chọn.

# OpenFilm CLI invocation contract — Windows

**CLI_REQUIRED**: đường điều khiển duy nhất cho OpenFilm trong P06–P21 là một OpenFilm CLI entrypoint đã được kiểm chứng. Đường dẫn tuyệt đối tới `.cmd`, `.exe` hay entrypoint được bản cài cung cấp; không gọi npx auto download, không coi Desktop/UI đủ thay CLI. OpenFilm Studio chỉ được mở tùy chọn bằng CLI `open`, không dùng UI để render thay cho CLI.

- P04 metadata read-only: A02 CLI, A03 Node>=22.2, A04 FFmpeg/FFprobe, A05 Chromium cache. Browser download first run và lệnh có side effect đều cần approval P05/P06. Không `openfilm doctor` ở P04 nếu side effect chưa kiểm.
- P06 sau duyệt: xác minh absolute binary path, version, `--help`, Node/FFmpeg/browser, cwd dưới WORKSPACE, log/exit code; dùng E2E 7 giây và QC. Cold start probe được duyệt trước, `renderClip` chỉ VERIFIED sau review.
- OpenFilm `look`/`render` luôn chạy với **cwd là thư mục chứa `film.html`**; `open` không được phép tự tạo bên ngoài `projects/` hoặc `qc/openfilm-e2e/fixture/`. Không import lời thoại từ `openfilm get` thay VieNeu.
- `look`: PNG/cache `.film/cache/look/` và evidence screenshots. `render [a-b] --out` khi bản CLI hỗ trợ, không ghi đè; `--fps`/`--workers` cũng chỉ khi `--help` của bản này xác minh. `--out` phải thuộc WORKSPACE; không được ghi đè nguồn hoặc bản master đã nghiệm thu.
- Tất cả lệnh có `packetId`, `deviceId`, workspace, workingDirectory, approvalId, command, args, exitCode, logs và output metadata; `exitCode=0` chưa đủ để tuyên bố video/audio/pass.
- Mã thoát dựa trên OpenFilm CLI docs: 0 success, 1 film/command error, 2 project/usage error; ghi giá trị thực, không tạo giả.
- Command arguments là array, tuyệt đối không shell expansion/`Invoke-Expression`/redirection `&` từ input; không chạy URL trong `open` nếu không có scope riêng.
- Remotion Master dùng OpenFilm CLI cho previs rồi Remotion CLI cho final; mode choice P08 không cho phép Desktop-only fallback.

Nguồn: https://openfilm.dev/docs/cli/ và https://github.com/openfilm/openfilm. CLI bản cài thực tế và help luôn ưu tiên trước tài liệu chung.
