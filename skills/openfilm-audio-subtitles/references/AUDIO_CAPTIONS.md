> v1.14.0: FINISH_FIRST_USER_REVIEW ưu tiên. Đây là công thức kỹ thuật/tham khảo; mọi đánh giá thẩm mỹ chỉ theo yêu cầu người dùng, mọi cổng QC legacy không chặn V01. OpenFilm CLI-first, GUI tùy chọn.

# Đồng bộ WAV, phụ đề và nhạc nền — ví dụ thiết kế

**Nguồn thời gian**: FilmData.frames, không tính thời gian bằng số chữ. OpenFilm Master dùng `<audio>` trong `film.html` và WebVTT; Remotion Master dùng `Sequence`/`Audio` đọc từ `public/` qua `staticFile()`. Ở cả hai chế độ, lời đọc đã được VieNeu sinh từ đúng text và đã đo FFprobe trước khi định timing cuối.

- Ví dụ thoại bắt đầu ở frame 270, FPS 30 → 9.0s. WAV nếu FFprobe báo 5.37s → `ceil(5.37*30)=162` frame, endFrame **432**. Đoạn `[270,432)` là 162 frame; không dùng 161 nếu cần bảo đảm không cắt đuôi. Cần kiểm đầu/cuối silence khi nghe.
- Chỉ tạo `captions.srt` được gắn trạng thái `VERIFIED` khi đã nghe/có cue alignment. SRT câu dài chưa có word-level alignment không được tuyên bố karaoke/word-sync.
- Font Việt cần kiểm ký tự: `ă â ê ô ơ ư đ Á À Ả Ã Ạ Ấ Ầ Ẩ Ẫ Ậ` khi thực render, không chỉ có font-family name.

Ví dụ luồng Remotion giả định `film.dialogues` đã được duyệt và assets đã ở `public/audio/`:

```tsx
import React from 'react';
import {Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';

const Dialogue: React.FC<{dialogues: Array<{id:string; startFrame:number; endFrame:number; audio:string}>}> = ({dialogues}) => <>
  {dialogues.map(d => <Sequence key={d.id} from={d.startFrame} durationInFrames={d.endFrame-d.startFrame}>
    <Audio src={staticFile(d.audio.replace(/^assets\//, ''))} volume={1}/>
  </Sequence>)}
</>;

function musicVolume(frame: number, dialogues: Array<{startFrame:number; endFrame:number}>): number {
  // Ví dụ curve duck 6-frame, cần nghe QC trước dùng production.
  const fade = 6;
  const edge = Math.min(1, ...dialogues.map(d => {
    if (frame >= d.startFrame && frame < d.endFrame) return 0;
    return Math.min(Math.abs(frame - d.startFrame), Math.abs(frame - d.endFrame)) / fade;
  }));
  return 0.07 + 0.11 * Math.max(0, Math.min(1, edge));
}
```

Ví dụ chuyển frame sang SRT:

```python
def srt_time(frame: int, fps: int) -> str:
    if fps <= 0 or frame < 0:
        raise ValueError("invalid frame/fps")
    ms = round(frame * 1000 / fps)
    hours, remainder = divmod(ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"
```

Khi FFprobe phát hiện file WAV khác sample rate/channels kỳ vọng, chỉ resample sau khi thống nhất workflow; giữ WAV gốc. Đo tiếng bằng FFmpeg `ebur128` và nghe thực tế; không coi -14 LUFS là cố định cho mọi nền tảng.
