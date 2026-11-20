---
name: openfilm-runtime-control
description: "Xác minh đường điều khiển OpenFilm Desktop/CLI trên Windows, ghi runtime profile có chứng cứ, khởi tạo film.html từ FilmData ngay P09 và kiểm tra khả năng preview trước P17."
---

# OpenFilm Runtime Control + Early Film Bootstrap (v1.8.0)

## A. Cổng khả năng runtime thật tại P06.08

Chạy **sau** P00–P05 và phê duyệt công đoạn P06. P04–P05 chỉ đọc inventory; không kết luận CLI có vì OpenFilm Desktop có sẵn. Khi user đã duyệt probe P06, kiểm tra các ứng dụng/CLI tại đường dẫn cụ thể trong workspace hoặc máy, phân biệt:

- `CLI_VERIFIED`: xác minh đường dẫn lệnh OpenFilm, phiên bản, `open`/`look`/`render` trong bản thực tế; lệnh `--help`/probe được phép và không tải ngầm. Những chức năng đã chạy/kiểm chứng có evidence độc lập. CLI đủ điều kiện mới dùng cho automation. **Không `npx -y` hay `@latest` để tránh tải tự động.**
- `DESKTOP_UI_VERIFIED`: không có CLI hoặc không dùng CLI, nhưng đã quan sát được OpenFilm Desktop mở thư mục, preview frame và xuất clip thật qua giao diện Windows với Remote Desktop Commander. Chỉ thao tác UI được xác nhận, không tự suy luận cửa sổ có chức năng tự động. Nếu không thao tác được GUI, `BLOCKED`.
- `UNVERIFIED/BLOCKED`: có app nhưng chưa xác minh method hoặc lỗi quyền, tương thích, tải trình duyệt; chỉ báo hiện trạng và phương án điều tra, không ghi kết quả hoàn thành.

`reports/openfilm/OPENFILM_RUNTIME_PROFILE.json` phải ghi `deviceId`, `workspace`, `mode`, đường dẫn runtime, phiên bản, `capabilities.openProject|inspectFrame|renderClip|openCanvas`, trạng thái, evidence paths thuộc workspace, approvalId, và phương thức kiểm chứng. Template `references/OPENFILM_RUNTIME_PROFILE_TEMPLATE.json`, kiểm trước khi chấp nhận bằng `references/validate_runtime_profile.py`; validator chỉ kiểm hợp đồng/metadata, không chứng minh khả năng thực tế. Đọc lại file sau lưu. `openCanvas` chỉ cần nếu chọn Canvas; nếu không là UNSUPPORTED hoặc UNVERIFIED không chặn làm phim.

**Phân công:** P06.08 profile → P06.09–P06.11 OpenFilm E2E fixture → P06.04 chốt runtime và môi trường. Khi GUI không có công cụ render tự động, cho người dùng thao tác thủ công trong phạm vi đã duyệt hoặc dừng rõ; không chuyển sang Remotion rồi ghi là OpenFilm PASS. Việc dùng Remotion Master cho phim dài là lựa chọn P08 riêng.

## B. Bootstrap project ở P09.06, trước P16

1. Đọc `projects/<film-id>/scene-data/film.json` có thật đã qua `validate_filmdata.py`. Gói `P09.06` được phê duyệt riêng rồi mới ghi trong workspace: `openfilm/film.html`, `openfilm/scenes/<shot-id>.html` **placeholder**. Dùng script `references/bootstrap_openfilm.py --workspace ... --project ... --film-data ... --create`. Trước khi duyệt gọi không `--create` để lập plan. Không ghi đè file hiện hữu hay vượt project root; đoạn generator này là scaffold, không phải scene hoàn thiện.
2. Khung hình theo `width/height`, `fps`; mỗi iframe đúng shot startFrame/fps và durationInFrames/fps, `#t=0,duration`; sử dụng đường dẫn tương đối. Các HTML placeholder ghi dấu `data-vhh-placeholder="true"`. Lưu JSON data, sha và nhật ký riêng theo checkpoint nếu ghi được.
3. P10 storyboard nhận dữ liệu, P14/P15 thay các trang placeholder bằng code thật **trong scope được duyệt**, trước P16 dùng `--check-ready` để từ chối bất cứ placeholder còn lại. Cảnh dùng GSAP/Three luôn deterministic `frame(t)`, không autoplay audio.
4. P16.06 chỉ preview khi project hợp lệ/không placeholder, `openProject=VERIFIED`, `inspectFrame=VERIFIED`; `look`/Studio UI theo profile đã kiểm, lưu screenshots actual. P17 chỉnh sửa **film.html hiện hữu**, bảo toàn track locked, overrides, timeline user vừa sửa; backup/hash trước ghi, không xây lại từ đầu.

Script không chuyển `film.html` thành JSX; Remotion Master vẫn dùng FilmData/file adapter riêng. Mọi `PASS` preview/render phải có file/output thật và evidence, không vì scaffold script trả exit 0.

## C. Canvas tùy chọn

Đọc `references/CANVAS_DECISION.md`. Mặc định `FILE_STORYBOARD`, mở `OPENFILM_CANVAS` chỉ khi `openCanvas=VERIFIED` và user duyệt, không gọi provider TTS/media hoặc dịch vụ trả phí. Canvas nằm ở P10.06/07, không là điều kiện để dùng OpenFilm HTML.

## Quy tắc CLI_ONLY_FOR_OPENFILM v1.9.0

`mode=cli` **là duy nhất** được phép đạt `READY_FOR_PREVIEW` hay `READY_FOR_RENDER`; `mode=desktop-ui` chỉ trạng thái lịch sử/UNVERIFIED. `OPENFILM_RUNTIME_PROFILE.json` phải khai báo `workingDirectory` tuyệt đối dưới workspace; khả năng CLI xác nhận bằng `--help` + project-bound look/E2E có phê duyệt. Nếu `open` khởi động Studio hoặc tải browser trong lần đầu, cần phê duyệt riêng. `openfilm look` tạo cache, `openfilm render` tạo MP4; ở P06.08 chưa được thực thi nếu chưa phê duyệt. CLI event theo `openfilm-cli-execution`; không dùng `npx`/UI-only fallback. P09 skeleton tạo bằng code offline đã duyệt; P16/P17 tiếp tục thao tác OpenFilm CLI trong cwd của project.
