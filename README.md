# shrinkvid 🎬➡️📦

**Shrink any video to an exact target size — WhatsApp, Discord, e-mail limits — with one command.**

No uploads. No watermarks. No "free trial". Your video never leaves your computer.

```bash
python shrinkvid.py holiday.mp4 --for whatsapp      # fits under 16 MB, ready to send
python shrinkvid.py clip.mov --to 10MB              # exact target size
python shrinkvid.py ./MyVideos --to 25MB            # whole folder, batch
```

```
▶ bigfull.mp4  (33.0 MB)  ->  target 16.0 MB
  ✔ bigfull_16mb.mp4: 14.7 MB (44% of original), 2634kbps video + 96kbps audio, 1 pass(es)
```

---

## Why?

Every day millions of people hit the same wall: *"video too large to send"*.
Online converters want you to **upload private videos to unknown servers** (and watermark
them). Video editors are overkill for "make this fit under 16 MB".

`shrinkvid` does exactly one thing: **hit your target size** while keeping the best
possible quality, entirely offline.

## How it works

1. Reads the real duration & audio tracks with `ffmpeg` (no `ffprobe` needed).
2. Splits your size budget into video + audio bitrates (audio capped so video keeps quality).
3. Encodes with 2-pass-style verification: if the result is still over target, it
   automatically retries at 720p → 480p → 360p → 240p until it fits.

## Presets

| Preset | Target | Typical use |
|---|---|---|
| `--for whatsapp` | 16 MB | WhatsApp status / DM |
| `--for discord` | 10 MB | Discord free-tier upload |
| `--for email` | 25 MB | Mail attachments |
| `--for instagram` | 60 MB | IG feed video |

Or pick any exact size: `--to 8MB`, `--to 700kb`, `--to 1.5GB`.

## Install

**1. Python 3.9+** and **ffmpeg** on your PATH:

```bash
# Windows
winget install Gyan.FFmpeg
# macOS
brew install ffmpeg
# Linux
sudo apt install ffmpeg
```

**2. Download `shrinkvid.py`** — that's the whole app:

```bash
curl -LO https://raw.githubusercontent.com/Volvox6767/shrinkvid/main/shrinkvid.py
```

No `pip install`. Single file, zero dependencies.

## Usage

```
python shrinkvid.py INPUT... --to SIZE | --for PRESET [--out FILE] [--overwrite] [--fast]

INPUT...        one or more video files and/or folders
--to SIZE       exact target, e.g. 16MB, 700kb, 1.5GB
--for PRESET    whatsapp | discord | email | instagram
--out FILE      output path (single input only)
--overwrite     replace the output file if it exists
--fast          fewer fallback resolutions (faster, usually enough)
```

Supported inputs: `mp4 mov mkv avi webm m4v ts wmv flv`.

Examples:

```bash
python shrinkvid.py video.mp4 --for discord              # video_10mb.mp4
python shrinkvid.py a.mp4 b.mp4 --to 25MB                # batch
python shrinkvid.py ./recordings --to 8MB --overwrite    # whole folder
```

## Notes

- Output is always `.mp4` (H.264 + AAC, `yuv420p`, `+faststart`) — plays everywhere: phones, TVs, WhatsApp, browsers.
- Files already under target are skipped (never re-encoded bigger).
- Windows terminals get UTF-8 output automatically (no more `UnicodeEncodeError`).
- Speed: a 1-minute 1080p video takes ~10–20 s on a laptop CPU.

## FAQ

**Does it upload my video anywhere?** No. 100 % local, ffmpeg only.

**Can it get under 1 MB?** Yes — quality gets mushy but it fits. Audio drops to 32 kbps first.

**Where's the audio?** Kept (stereo AAC). Only dropped if the source has none.

---

Made with ❤ by **Ahmet Gedik** — [instagram.com/ahmetgedik67](https://www.instagram.com/ahmetgedik67)
Follow on Instagram for more free everyday tools.

License: [MIT](LICENSE)
