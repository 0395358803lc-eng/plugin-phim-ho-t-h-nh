---
name: openfilm-canvas
description: "Thiết kế storyboard, khung hình, nhân vật nhất quán, voice-over trên OpenFilm Canvas khi chuẩn bị video hoạt hình."
---

> Kỹ năng OpenFilm gốc, được giữ nội dung và đổi tên kỹ năng để tích hợp vào plugin Video-hoạt-hình. Chỉ chạy các lệnh khi CLI OpenFilm thực sự tồn tại trên máy có quyền truy cập. Tên và nhãn lệnh trong nội dung dưới đây thuộc OpenFilm, không phải lệnh có sẵn của ChatGPT.

# The canvas

The canvas is a board beside the edit: notes, the project's files, and nodes that make a picture, a clip or a sound,
wired into each other. Nothing on it is in the film until it is put on the timeline. A node is pointed at, by the
person and by you, with a link to its board's file and its id: `.film/canvas.json#n7`. A project can have several
canvases; your steps go to the one the person has open.

`openfilm canvas` prints the board. `openfilm canvas apply '<steps>'` adds, changes, wires and removes nodes, all at
once, and the person sees it at once; `openfilm canvas --help` lists the steps. `openfilm canvas add <file…>` puts
files of the project on it in a row.

## Laying out what the person asks for

- **A storyboard or shots**: one row per shot, left to right: a note (what happens, in the person's words), a picture
  node wired from it, and a video node wired from the picture with `opts.mode: "first"`. Wire every video into one
  `cut`, in order: its "Put on the timeline" sends the clips in that order. With many shots, keep each in a group
  named after it (`around`).
- **A character who looks the same in every shot**: a note of who they are, a picture node with `preset: "portrait"`
  wired from it, then `fullBody`, `expressions` and `turnaround16` pictures each wired from the note and the portrait,
  in a group named after them. Wire the portrait into every shot's picture and video (`opts.mode: "refs"`).
- **A voice-over**: a `tts` node whose prompt is the line to speak, with `opts.voice` a voiceId from
  `openfilm get voice` that suits the speaker.
- **A node's prompt**: in English unless the person writes otherwise; what is seen, the light and the camera, not
  the story's meaning.

Lay things out and leave the making to the person: they press Make, or a group's Make all. Make a node only when
they ask: with `openfilm get`, then add the file as its version (`"op": "version"`). Say what you laid out and what to
press.

A making node says what it makes with (`--via`, `--model` and its options): what the person picked. Make it anew with
the same, at the same ratio, quality and size, unless the person names another model, and say which you used.

## Canvas không bắt buộc (v1.8.0)

Trước lệnh Canvas ở P10 đọc `openfilm-runtime-control/references/CANVAS_DECISION.md`. `FILE_STORYBOARD` là mặc định: tạo storyboard từ file trong project không cần CLI Canvas. `OPENFILM_CANVAS` chỉ nếu `openCanvas=VERIFIED` với evidence + người dùng phê duyệt thao tác; `openfilm canvas apply` có thể sửa board nên phải có approval scope. Canvas node `tts`/`voice-over` gốc chỉ là chức năng mẫu của upstream; với dự án VieNeu **không tạo hoặc chạy** node này, không bấm Make/Make all gây sinh media hoặc chi phí. Thay bằng liên kết tới WAV VieNeu hợp lệ, không thay nguồn lời thoại. Nếu CLI không có, dùng file storyboard, báo SKIPPED_CANVAS.

## Canvas v1.9.0 — chỉ OpenFilm CLI

Khi user chọn Canvas tại P10 và capability `openCanvas=VERIFIED` của **CLI** (không phải UI-only), dùng `openfilm canvas`/`canvas apply` bản CLI đã xác minh, cwd đúng project và có phê duyệt ghi board. Nếu thiếu CLI/canvas subcommand hoặc permission, dùng `FILE_STORYBOARD`, báo `SKIPPED_CANVAS` có bằng chứng; không bật GUI Desktop để thay CLI. Nút Make/Make all/provider/TTS bị chặn theo voice-source lock.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate
M2 chỉ PASS khi ảnh storyboard/nhân vật/bối cảnh thực sự chuyển đến ChatGPT dưới dạng hình ảnh và được quan sát/ghi nhận; text Canvas node, note/JSON và success code chưa đủ. Nếu Canvas không xuất PNG được, dùng file storyboard với ảnh PNG; vẫn áp dụng `openfilm-visual-inspection`.
