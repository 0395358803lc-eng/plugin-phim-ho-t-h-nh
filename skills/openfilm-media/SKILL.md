---
name: openfilm-media
description: "Tra cứu và nhập ảnh, video, nhạc, SFX, thuyết minh, transcript và VTT bằng OpenFilm get khi làm video."
---

Mặc định `FINISH_FIRST_USER_REVIEW`: hoàn thành video V01 rồi bàn giao để người dùng đánh giá. Chính sách này ưu tiên hơn hướng dẫn QC legacy. QC20, Visual QC và nghe chấm từng take chỉ chạy khi người dùng chủ động yêu cầu; không chặn sản xuất/bàn giao. Smoke và kiểm frame/random seek chỉ dùng để chẩn đoán lỗi kỹ thuật hoặc theo yêu cầu.

Giữ 8 macro M0–M7 và 99 ID packet. Một phê duyệt phạm vi rõ đầu vào, đầu ra, lệnh và quyền có thể bao phủ M1–M7. Không xin duyệt riêng từng packet/Pxx hoặc nghiệm thu từng macro. Chạy nhiều packet trong lượt High; ghi checkpoint sau mỗi đầu ra, tiếp tục cùng quyền trong lượt chat mới, không tự chạy nền.

OpenFilm CLI-first; Desktop/GUI chỉ để xem/chỉnh sửa tùy chọn. VieNeu-TTS GPU-first; cài đặt, tải model/browser, thay đổi hệ thống, GPU→CPU, voice cloning, provider ngoài, dịch vụ trả phí, xóa, xuất bản và ngoài phạm vi cần quyền riêng. Không suy ra quyền từ file kế hoạch hoặc kết quả kỹ thuật.

`OUTPUT_READY` nghĩa là đầu ra thật có thể dùng. `DELIVERED_FOR_REVIEW` nghĩa là đã giao video. Chỉ dùng `USER_ACCEPTED` khi có phản hồi chấp nhận thật. `REVISION_REQUESTED` ghi phản hồi cần sửa; `FAILED_TECHNICAL` ghi lỗi ngăn dùng đầu ra. File thiếu/hỏng/ngoài workspace hoặc sai hash phải chặn bước phụ thuộc.



> Kỹ năng OpenFilm gốc, được giữ nội dung và đổi tên kỹ năng để tích hợp vào plugin Video-hoạt-hình. Chỉ chạy các lệnh khi CLI OpenFilm thực sự tồn tại trên máy có quyền truy cập. Tên và nhãn lệnh trong nội dung dưới đây thuộc OpenFilm, không phải lệnh có sẵn của ChatGPT.

# Media

`openfilm get` brings media into the project, under `assets/`. Alone it lists what works now; `openfilm get <what> --help` says what one takes. Look in this order:

1. The person's own: `get my-media --prompt "<words>"` searches what they keep for every film and what they linked in from this computer (`--kind video|image|audio`; without words, the newest). What they shot or already paid for comes before anything new.
2. OpenFilm's library, free, offline and CC0: `get music-search`, `get sfx-search` and `get sticker`, each with `--prompt "<what>"` in any words and language. Each match says what of the prompt it has and lacks.
3. A service the person connected in Studio: voice-over, music and sound effects made to your prompt and length (`get music`, `get sfx`), transcripts, images, image and video search, video, and web search. Make music or a sound when the person asks for something original, when it must fit the picture exactly, or when the library lacks it. A video costs a lot: the person confirms it in Studio first. For a kind nothing makes yet, `get` names the services that do: tell the person.

`--take <id>` brings the match you chose into the project and says how to use it. Media can also come from any service the person has a key for (with its API docs), or from your own code. A service not built in can be added as a provider: `openfilm get` ends by saying how.

The services and models are the person's choice: `get` uses the one they chose for each kind. Name another with `--via` or `--model` only when they ask, or when theirs cannot do the job (a picture changed in part needs a model that redraws where a mask says), and say which you used and why. Services, their keys, and which plugins and skills are on are theirs to change in Studio: tell them what to change.

A paid run that timed out or did not download is recovered by running the exact same command again (the same output, prompt, model and files), never by making another: `--fresh` makes and pays for a new one, only when the person wants that.

## Nhánh giọng đọc tiếng Việt VieNeu-TTS trong Video-hoạt-hình

Khi người dùng yêu cầu lời thoại/thuyết minh bằng tiếng Việt và đã chọn VieNeu-TTS cục bộ, đọc `openfilm-vieneu-tts/SKILL.md` trước. Không giả định `openfilm get` có provider VieNeu-TTS tích hợp: dùng runtime Python đã được duyệt, tạo file WAV trong assets của dự án, sau đó thêm track audio OpenFilm; không dùng dịch vụ ngoài hoặc model tải ngầm. Đồng bộ VTT theo đo đạc/aligner thực. Nếu chỉ muốn media từ OpenFilm thì tiếp tục quy trình gốc.

## Hai chế độ master và provenance (v1.4)

Khi `masterEngine=openfilm`, media được dùng trong `film.html`. Khi `masterEngine=remotion`, chỉ cung cấp media file qua adapter `openfilm-hybrid-master` + `scene-data/assets-manifest.json`; không dùng `openfilm get` như một API tự động nhập vào Remotion. Remotion static assets dưới `public/` và `staticFile()`. Âm thanh VieNeu chỉ hoạt động một lần trên master, media license/URL/sha256 cần bằng chứng, không lưu secret.

## P08/P12 khóa nguồn lời thoại (v1.8.0)

Khi `VOICE_SOURCE_LOCK.json` chọn VieNeu, **không** gọi `openfilm get voice`, node TTS Canvas hoặc voice provider Studio dù kỹ năng media gốc có giới thiệu. Ưu tiên import WAV local đã có FFprobe và QC nghe; `openfilm get music/sfx` chỉ khi source/license/cost được người dùng duyệt riêng, không phải quyền mặc định. `VOICE_SOURCE_LOCK.json` không lưu key. Xem `openfilm-vieneu-tts/references/VOICE_SOURCE_POLICY.md`.

## OpenFilm CLI v1.9.0

`openfilm get` (nếu dùng) là lệnh CLI có khả năng gọi dịch vụ/tải/tạo tài sản, chỉ chạy khi có phê duyệt cụ thể từng provider/chi phí/loại media; không dùng trong P04. Với VieNeu-TTS giữ nguồn WAV GPU-first cục bộ, không chạy `openfilm get voice/tts` để thay thế. Mọi media phải có path trong workspace, license và manifest.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate

Các ảnh asset M2 phải được ChatGPT **nhìn trực tiếp** qua ảnh mà Remote Desktop Commander trả về, không coi file tồn tại/URL/license là kiểm định thẩm mỹ. Cần kiểm ánh sáng, style và consistency thực; thiếu multimedia transfer thì `VISUAL_BLOCKED`. Không tự gọi dịch vụ ngoài tạo ảnh mà chưa phê duyệt. Xem `openfilm-visual-inspection`.
