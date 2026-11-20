> v1.14.0: FINISH_FIRST_USER_REVIEW ưu tiên. Đây là công thức kỹ thuật/tham khảo; mọi đánh giá thẩm mỹ chỉ theo yêu cầu người dùng, mọi cổng QC legacy không chặn V01. OpenFilm CLI-first, GUI tùy chọn.

# P09.06 → P16.06 → P17.07: Một project OpenFilm duy nhất

FilmData ở `projects/<film-id>/scene-data/film.json` là *nguồn quy ước của plugin*, không phải OpenFilm tự sinh. P09.06 chuyển dữ liệu đã kiểm chứng thành:

```text
projects/<film-id>/
  scene-data/film.json
  openfilm/
    film.html                 # dựng khung scene + thời gian từ P09
    scenes/<shot-id>.html     # PLACEHOLDER từ P09; thay bằng cảnh đã duyệt ở P14/P15
    assets/                   # chỉ khi có media thật
```

- Đặt kích thước film bằng `<meta name="viewport" ...>`. Một `<section>` hình có `<iframe id="shotId" src="scenes/shotId.html#t=0,duration" at="start">` cho mỗi shot, không chồng trên cùng track.
- `scenes/*.html` placeholder có DOM marker `data-vhh-placeholder="true"`; **mục đích chỉ kiểm file/đường dẫn, không chứng minh storyboard hoặc render đã đạt**. Nếu render được placeholder phải ghi đó là probe, không gắn `P16 QC PASS`.
- `P14.06` xóa placeholder bằng cách thay scene đã được phê duyệt, không chép code demo cho phim thực. `P16.06` chạy script với `--check-ready` và OpenFilm `look` hoặc Studio đã verify, chặn nếu chưa có hình thật. `P17.07` giữ nguyên film.html, thêm audio, caption `<track kind="captions">`, color, SFX, nhạc nền; phải bảo vệ locked/overrides.
- Khi `masterEngine=remotion`, OpenFilm là previs (không phải final timeline); vẫn cần kiểm tra project khả dụng nếu đã chọn sử dụng nó. Không chuyển scene HTML sang JSX giả định có API.
- Các thao tác ghi phải nằm trong workspace đã chọn và có `planApprovalId`, báo thay đổi/hashes trong checkpoint. Nếu project đã tồn tại, script không overwrite; cần kế hoạch cập nhật/reconcile được duyệt.
