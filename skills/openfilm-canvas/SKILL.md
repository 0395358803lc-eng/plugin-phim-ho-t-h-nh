---
name: openfilm-canvas
description: "Tham khảo legacy OpenFilm Canvas theo yêu cầu; storyboard sản xuất mặc định là dữ liệu JSON/Markdown/FilmData không tạo picture nodes."
---

# OpenFilm Canvas — chỉ tùy chọn v1.14.2

P10 mặc định bắt buộc `FILE_DATA_STORYBOARD`, đọc `openfilm-storyboard-data/SKILL.md`, tạo `storyboard.json` + `STORYBOARD.md`. **Không dùng Canvas để sinh ảnh storyboard**, không tạo picture/video/TTS nodes, portrait, expressions, turnaround, Make/Make all; không rasterize hay handoff ZIP. Canvas không thuộc đường phụ thuộc mặc định của engine OpenFilm CLI hay Remotion.

Nếu user yêu cầu sử dụng Canvas như bảng note để xem dữ liệu, chỉ thao tác note/text/link dữ liệu khi OpenFilm CLI Canvas capability VERIFIED và scope ghi board được duyệt riêng. Không có Canvas vẫn tiếp tục; Remotion Master không cần OpenFilm CLI Canvas. Không suy ra ảnh trong node hay chi phí provider được cấp quyền. Các thao tác trong `references/openfilm-canvas-original-SKILL.md` là tư liệu upstream, **không được chạy trên đường sản xuất mới**.

Mục tiêu: V01 rồi bàn giao user đánh giá; kiểm file kỹ thuật, không nghiệm thu ảnh từng shot.
