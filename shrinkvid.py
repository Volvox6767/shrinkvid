#!/usr/bin/env python3
"""
shrinkvid — shrink any video to an exact target size (WhatsApp, Discord, e-mail...).

Single file, no dependencies: only needs ffmpeg on your PATH.
  python shrinkvid.py video.mp4 --to 16MB
  python shrinkvid.py clip.mov --for whatsapp
  python shrinkvid.py ./myfolder --to 10MB --overwrite

Author : Ahmet Gedik  (https://www.instagram.com/ahmetgedik67)
License: MIT
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

__version__ = "1.0.0"
AUTHOR = "Ahmet Gedik"
INSTAGRAM = "https://www.instagram.com/ahmetgedik67"

PRESETS = {  # conservative real-world limits
    "whatsapp": "16MB",
    "discord": "10MB",
    "telegram": "50MB" if False else "2000MB",  # telegram is huge; keep sane default
    "email": "25MB",
    "instagram": "60MB",  # IG feed 15min/60MB-ish
}
AUDIO_KBPS_CAP = 128


def banner() -> str:
    return (
        "\n  shrinkvid — shrink videos to an exact target size\n"
        f"  by {AUTHOR}  |  {INSTAGRAM}\n"
        "  -------------------------------------------------\n"
    )


# ------------------------------------------------------------------ ffmpeg
def find_ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg  # optional convenience

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    hint = "ffmpeg not found.\nInstall it first:\n  Windows : winget install Gyan.FFmpeg   (then reopen the terminal)\n  macOS   : brew install ffmpeg\n  Linux   : sudo apt install ffmpeg"
    sys.exit(hint)


def ffprobe(path: Path, ffmpeg: str) -> dict:
    """Probe duration/streams using the bundled ffmpeg (no ffprobe needed)."""
    out = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(path), "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
    if not m:
        raise RuntimeError(f"could not read duration of {path.name}")
    dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    audio = bool(re.search(r"Stream #\d+:\d+.*: Audio:", out))
    return {"duration": dur, "has_audio": audio}


def parse_size(text: str) -> int:
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*([kKmMgG]?[bB])\s*", text)
    if not m:
        raise argparse.ArgumentTypeError(f"invalid size: {text!r} (examples: 16MB, 700kb, 1.5GB)")
    val, unit = float(m.group(1)), m.group(2).lower()
    mult = {"b": 1, "kb": 1_000, "mb": 1_000_000, "gb": 1_000_000_000}[unit]
    return int(val * mult)


# ------------------------------------------------------------------ encoding
def budget(total: int, duration: float, has_audio: bool) -> tuple[int, int]:
    """Split target bytes into (video_kbps, audio_kbps) with 4% container headroom.
    Audio gets at most ~25% of the budget (capped 96 kbps) so video keeps quality."""
    usable = total * 0.96
    if not has_audio:
        return max(8, int(usable * 8 / duration / 1000)), 0
    audio_k = min(96, max(32, int(usable * 0.25 * 8 / duration / 1000)))
    video_bytes = max(usable - audio_k * 1000 * duration / 8, usable * 0.4)
    return max(8, int(video_bytes * 8 / duration / 1000)), audio_k


def encode(ffmpeg: str, src: Path, dst: Path, vk: int, ak: int, height: int | None) -> None:
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(src)]
    vf = "scale=-2:%d" % height if height else "scale=trunc(iw/2)*2:trunc(ih/2)*2"
    cmd += ["-vf", vf, "-c:v", "libx264", "-preset", "medium", "-b:v", f"{vk}k",
            "-maxrate", f"{int(vk * 1.45)}k", "-bufsize", f"{int(vk * 2)}k",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    if ak:
        cmd += ["-c:a", "aac", "-b:a", f"{ak}k", "-ac", "2"]
    else:
        cmd += ["-an"]
    cmd += [str(dst)]
    subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")


MAX_HEIGHTS = [None, 1080, 720, 480, 360, 240]


def compress(ffmpeg: str, src: Path, dst: Path, target: int, fast: bool) -> dict:
    info = ffprobe(src, ffmpeg)
    dur = info["duration"]
    if dur <= 0:
        raise RuntimeError(f"zero duration: {src.name}")

    vk, ak = budget(target, dur, info["has_audio"])
    attempts, heights = 0, ([None, 720, 480] if fast else MAX_HEIGHTS)
    for h in heights:
        attempts += 1
        encode(ffmpeg, src, dst, vk, ak, h)
        size = dst.stat().st_size
        if size <= target:
            return {"size": size, "video_kbps": vk, "audio_kbps": ak,
                    "height": h or "source", "attempts": attempts}
        # still too big: drop quality ~ proportionally and retry at lower res
        vk = max(8, int(vk * size / target * 0.92))
    return {"size": dst.stat().st_size, "video_kbps": vk, "audio_kbps": ak,
            "height": h or "source", "attempts": attempts, "warning": "could not reach target"}


def human(n: float) -> str:
    """Decimal units (1 MB = 1_000_000 B) to match --to parsing and app limits."""
    for u in ("B", "KB", "MB", "GB"):
        if n < 1000 or u == "GB":
            return f"{int(n)} B" if u == "B" else f"{n:.1f} {u}"
        n /= 1000
    return f"{n:.1f} GB"


# ------------------------------------------------------------------ cli
def size_tag(target: int) -> str:
    """300000 -> '300kb', 16000000 -> '16mb', 1500000000 -> '1.5gb'."""
    if target >= 1_000_000_000:
        v, u = target / 1_000_000_000, "gb"
    elif target >= 1_000_000:
        v, u = target / 1_000_000, "mb"
    else:
        v, u = target / 1_000, "kb"
    s = (f"{v:.1f}").rstrip("0").rstrip(".")
    return f"{s}{u}"


def unique_out(src: Path, tag: str, overwrite: bool) -> Path:
    out = src.with_name(f"{src.stem}_{tag}.mp4")
    if out.exists() and not overwrite:
        for i in range(2, 100):
            cand = src.with_name(f"{src.stem}_{tag}_{i}.mp4")
            if not cand.exists():
                out = cand
                break
    return out


def is_video(p: Path) -> bool:
    return p.suffix.lower() in {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".ts", ".wmv", ".flv"}


def collect(inputs: list[str]) -> list[Path]:
    files: list[Path] = []
    for item in inputs:
        p = Path(item)
        if p.is_dir():
            files += [f for f in sorted(p.iterdir()) if f.is_file() and is_video(f)]
        elif p.exists():
            files.append(p)
        else:
            print(f"  ! not found: {item}")
    return files


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="shrinkvid",
        description="Shrink videos to an exact target size (WhatsApp/Discord/email limits) using ffmpeg.",
        epilog=f"by {AUTHOR} — {INSTAGRAM}",
    )
    ap.add_argument("inputs", nargs="+", help="video file(s) or folder(s)")
    ap.add_argument("--to", type=parse_size, help="target size, e.g. 16MB, 25MB, 700kb")
    ap.add_argument("--for", dest="preset", choices=sorted(k for k in PRESETS if k != "telegram"),
                    help="preset limit")
    ap.add_argument("--out", help="output path (single input only)")
    ap.add_argument("--overwrite", action="store_true", help="overwrite existing output")
    ap.add_argument("--fast", action="store_true", help="fewer fallback resolutions (faster)")
    ap.add_argument("--version", action="version", version=f"shrinkvid {__version__}")
    args = ap.parse_args()

    target = args.to
    if args.preset:
        if target:
            ap.error("use either --to or --for, not both")
        target = parse_size(PRESETS[args.preset])
    if not target:
        ap.error("give a target: --to 16MB  or  --for whatsapp")

    print(banner())
    files = collect(args.inputs)
    if not files:
        print("no video files found.")
        return 1
    if args.out and len(files) > 1:
        ap.error("--out works with a single input only")

    ffmpeg = find_ffmpeg()
    ok = fail = 0
    for src in files:
        out = Path(args.out) if args.out else unique_out(src, size_tag(target), args.overwrite)
        print(f"\n▶ {src.name}  ({human(src.stat().st_size)})  ->  target {human(target)}")
        if src.stat().st_size <= target and not args.out:
            print(f"  ✔ already {human(src.stat().st_size)} (≤ target) — nothing to do.")
            ok += 1
            continue
        if src.stat().st_size <= target and args.out:
            shutil.copyfile(src, out)
            print(f"  ✔ already ≤ target — copied to {out.name}.")
            ok += 1
            continue
        try:
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / "out.mp4"
                res = compress(ffmpeg, src.resolve(), tmp, target, args.fast)
                shutil.move(str(tmp), str(out))
            pct = 100 * res["size"] / src.stat().st_size
            warn = f"  ⚠ {res['warning']}" if res.get("warning") else ""
            print(f"  ✔ {out.name}: {human(res['size'])} ({pct:.0f}% of original), "
                  f"{res['video_kbps']}kbps video"
                  + (f" + {res['audio_kbps']}kbps audio" if res["audio_kbps"] else ", no audio")
                  + f", {res['attempts']} pass(es){warn}")
            ok += 1
        except subprocess.CalledProcessError as e:
            print(f"  ✘ ffmpeg failed for {src.name}: {(e.stderr or '').strip()[-300:]}")
            fail += 1
        except Exception as e:
            print(f"  ✘ {src.name}: {e}")
            fail += 1

    print(f"\ndone: {ok} ok, {fail} failed.")
    print(f"\nmade with ❤ by {AUTHOR} — {INSTAGRAM}")
    return 0 if fail == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
