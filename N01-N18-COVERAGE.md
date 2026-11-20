# Ma trận nâng cấp N01–N18 · Video-hoạt-hình v1.4.0

Nguồn lựa chọn nâng cấp: `deep-research-report (1).md`, do người dùng cung cấp 19/11/2026. Đây là **tài liệu hướng dẫn và ví dụ kỹ thuật** cho plugin skills-only; không phải tuyên bố máy Windows đã cài hay video đã render. Các ô `INTEGRATED_IN_SKILL` chỉ chứng minh skill hướng dẫn hành vi, `RUNTIME_UNVERIFIED` nói rõ tính năng chưa được thử end-to-end trên PC.

| ID | Hạng mục đã duyệt | Skill sở hữu | Bằng chứng file/kiểm tra | Trạng thái |
|---|---|---|---|---|
| N01 | OpenFilm Master hoặc Remotion Master | `openfilm-hybrid-master` | `SKILL.md` mode selector | INTEGRATED_IN_SKILL |
| N02 | OpenFilm–Remotion file adapter | `openfilm-hybrid-master` | `references/ADAPTER.md` | INTEGRATED_IN_SKILL |
| N03 | FilmData schema JSON/TS | `openfilm-filmdata` | `film-data.schema.json`, `validate_filmdata.py` | INTEGRATED_IN_SKILL |
| N04 | Single master frame timeline | `openfilm-filmdata` | Python validator + 90s data fixture | INTEGRATED_IN_SKILL |
| N05 | Asset manifest / provenance | `openfilm-filmdata` | `openfilm-sample-90s/references/assets-manifest.json` | INTEGRATED_IN_SKILL |
| N06 | Hạt Mầm Ánh Sáng 90s | `openfilm-sample-90s` | `references/film.json`: 6 shots/7 dialogues; audio not generated | SAMPLE_SOURCE_ONLY |
| N07 | R3F + @remotion/three | `openfilm-remotion-r3f` | `references/R3F_EXAMPLE.tsx` | RUNTIME_UNVERIFIED |
| N08 | GSAP seek by Remotion frame | `openfilm-gsap` | v1.4 appended section | INTEGRATED_IN_SKILL |
| N09 | WebGL headless ANGLE/QC | `openfilm-remotion-r3f` | `SKILL.md` + R3F example | RUNTIME_UNVERIFIED |
| N10 | TTS duration from WAV FFprobe | `openfilm-audio-subtitles`, `openfilm-vieneu-tts` | `AUDIO_CAPTIONS.md` + TTS skill | RUNTIME_UNVERIFIED |
| N11 | Vietnamese SRT/VTT/font validation | `openfilm-audio-subtitles` | `AUDIO_CAPTIONS.md` | RUNTIME_UNVERIFIED |
| N12 | Music ducking / audio mix | `openfilm-audio-subtitles` | `AUDIO_CAPTIONS.md` | RUNTIME_UNVERIFIED |
| N13 | Render profile 16:9/9:16 codec | `openfilm-render-profiles` | `references/PROFILES.json` | INTEGRATED_IN_SKILL |
| N14 | QC20 acceptance framework | `openfilm-qc-advanced` | `references/QC20.md` | INTEGRATED_IN_SKILL |
| N15 | Adaptive hardware / concurrency | `openfilm-render-profiles` | `SKILL.md` hardware guidance | RUNTIME_UNVERIFIED |
| N16 | Deterministic random seek checks | `openfilm-qc-advanced` | `SKILL.md` tests specification | RUNTIME_UNVERIFIED |
| N17 | Dependency lock & licenses | `openfilm-render-profiles` | `LICENSE_DEPENDENCIES.md` + P04/P05 B05–B10 | INTEGRATED_IN_SKILL |
| N18 | 5-second E2E smoke test gate | `openfilm-qc-advanced` | `SKILL.md` SMOKE-01–03 | RUNTIME_UNVERIFIED |

## Quy tắc nghiêm ngặt

1. P00–P05 không thay đổi thứ tự. Không cài trước khi trình danh mục và nhận phê duyệt rõ.
2. B05–B10 chỉ kiểm/cài khi nhu cầu Remotion Master với React/R3F/TSX thực sự được chọn. Không tự `npx ...@latest`.
3. OpenFilm Master vẫn mặc định để giữ cách làm cũ. Chế độ Remotion Master không có API chuyển đổi source trực tiếp; dùng các file JSON, WAV, MP4 đã kiểm.
4. Schema check không tương đương đủ media: file sample thiếu WAV, SVG, GLB; `--check-assets` phải thất bại cho đến khi có media thật.
5. Cần xác minh render trên máy Windows, audio nghe trực tiếp hoặc upload lại và phê duyệt trước khi gọi nghiệm thu end-to-end.
