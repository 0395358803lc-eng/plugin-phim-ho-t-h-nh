# Video-hoạt-hình v1.14.3 — Code-only, Storyboard dữ liệu, Dual Engine

Quy trình hiện tại: P00–P06 máy/workspace/runtime → P07–P09 kịch bản & chọn engine **OpenFilm CLI / Remotion** → P10 storyboard JSON/Markdown/FilmData (không ảnh) → P11 asset/code scene cần thiết (không PNG/ZIP storyboard) → P12–P13 VieNeu-TTS/WAV/phụ đề khi có lời thoại → P14–P17 code hoạt hình/timeline **theo engine đã chọn** → P19 render V01 → P21 giao người dùng đánh giá; chỉ P20 sau phản hồi.

Mặc định Finish First, 8 macro và 99 packet ID nội bộ. Không QC thẩm mỹ trong đường phụ thuộc mặc định. Kiểm file/hash/codec để đảm bảo đầu ra có thể dùng.

- **A OpenFilm CLI:** HTML/SVG/Canvas/GSAP/Three.js, OpenFilm timeline + render.
- **B Remotion:** React/TSX/R3F, Remotion Composition + renderer/CLI trực tiếp. Không bắt OpenFilm CLI.

Đọc `skills/video-hoat-hinh/SKILL.md`, `skills/openfilm-storyboard-data/SKILL.md` và `skills/openfilm-production-p06-p21/references/STAGE_DEFINITIONS.json` để thực hiện. Tất cả thao tác cài/download/CPU fallback/ngoài scope cần quyền riêng. Ảnh từ user chỉ nhập nếu phim thực sự cần; không có ảnh storyboard.

Phiên bản trước và các skill legacy khác giữ nguyên khi áp bản vá này; chính sách v1.14.3 ưu tiên trong vùng chồng chéo.
