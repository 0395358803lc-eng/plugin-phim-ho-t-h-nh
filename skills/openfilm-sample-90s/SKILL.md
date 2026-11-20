---
name: openfilm-sample-90s
description: "Dùng bộ dữ liệu dự án mẫu Hạt Mầm Ánh Sáng 90 giây/30fps/6 shots/7 lời thoại để kiểm thử FilmData và chuẩn bị smoke hybrid mà chưa giả định đã có video hay model." 
---

# Dự án mẫu Hạt Mầm Ánh Sáng (N06)

Đây là **fixture kỹ thuật/brief hoàn chỉnh ở mức kịch bản và dữ liệu frame**, không phải phim đã sản xuất hoặc đã render. Dự án 90s, 1920×1080, 30fps = 2700 frames, nhân vật robot An, phát hiện hạt sáng rồi mang ra vườn 3D. Nội dung lấy từ báo cáo đính kèm và **sửa điểm thiếu dữ liệu của đoạn mã ví dụ**: tạo đủ 6 shots/7 dialogues nhất quán và tên WAV theo shot, dù **chưa có audio/GLB/texture**.

| Shot | Frame [start,end) | Nội dung | Công nghệ |
|---|---:|---|---|
| S01 | [0,240) | Title/phòng thí nghiệm | GSAP/SVG |
| S02 | [240,720) | Robot An thấy hạt sáng | GSAP/SVG |
| S03 | [720,1260) | Mang hạt qua hành lang | GSAP |
| S04 | [1260,1800) | Vào vườn | Three/R3F |
| S05 | [1800,2340) | Hạt nảy mầm | Three/R3F + GSAP |
| S06 | [2340,2700) | Cây phát sáng/kết | Three/R3F + GSAP |

**Dữ liệu:** `references/film.json` + `references/assets-manifest.json`; có `7` câu thoại gồm narrator ở S06, thời gian chỉ là dự kiến. **Không** bảo đảm các câu khớp độ dài WAV vì chưa chạy VieNeu. Khi có nguồn audio thực: đo FFprobe, cập nhật endFrame đúng, xử lý overlap/gap có duyệt.

Các dữ liệu trong file JSON là source fixture. Mã `openfilm-filmdata/references/validate_filmdata.py` kiểm thử cấu trúc và frame: PASS cấu trúc có nghĩa các shot liên tục, **không** chứng minh asset tồn tại, TTS đúng, WebGL chạy hoặc phim đã render. Chạy `--check-assets` khi đã có media; fixture sạch ban đầu sẽ FAIL vì thiếu WAV và các asset chính.

Quy trình nghiệm thu demo: P00–P05 máy/đường dẫn → duyệt chọn master và cài nếu cần → tạo assets thật → VieNeu 7 WAV đã duyệt → data validation (bắt đầu phụ đề) → smoke 5s → build scenes → render draft 90s → QC20 → master MP4+SRT. Chỉ ghi PASS cho mỗi gate khi đã kiểm chứng trên máy đã chọn.
