# shrinkvid 🎬➡️📦

**EN | Shrink any video to an exact target size — WhatsApp, Discord, e-mail limits — with one command.**
**TR | VideoKüçült — Herhangi bir videoyu tek komutla hedef boyuta sıkıştırır — WhatsApp, Discord, e-posta limitlerine uydurur.**

No uploads. No watermarks. No "free trial". Your video never leaves your computer.
Yükleme yok. Filigran yok. "Ücretsiz deneme" yok. Videonuz bilgisayarınızdan hiç çıkmaz.

```bash
python shrinkvid.py holiday.mp4 --for whatsapp      # EN: fits under 16 MB | TR: 16 MB altına sığdırır
python shrinkvid.py clip.mov --to 10MB              # EN: exact target size | TR: kesin hedef boyut
python shrinkvid.py ./MyVideos --to 25MB            # EN: whole folder, batch | TR: tüm klasör, toplu
```

```
▶ bigfull.mp4  (33.0 MB)  ->  target 16.0 MB
  ✔ bigfull_16mb.mp4: 14.7 MB (44% of original), 2634kbps video + 96kbps audio, 1 pass(es)
```

---

## 🇬🇧 English

### Why?

Every day millions of people hit the same wall: *"video too large to send"*.
Online converters want you to **upload private videos to unknown servers** (and watermark
them). Video editors are overkill for "make this fit under 16 MB".

`shrinkvid` does exactly one thing: **hit your target size** while keeping the best
possible quality, entirely offline.

### How it works

1. Reads the real duration & audio tracks with `ffmpeg` (no `ffprobe` needed).
2. Splits your size budget into video + audio bitrates (audio capped so video keeps quality).
3. Encodes with 2-pass-style verification: if the result is still over target, it
   automatically retries at 720p → 480p → 360p → 240p until it fits.

### Presets

| Preset | Target | Typical use |
|---|---|---|
| `--for whatsapp` | 16 MB | WhatsApp status / DM |
| `--for discord` | 10 MB | Discord free-tier upload |
| `--for email` | 25 MB | Mail attachments |
| `--for instagram` | 60 MB | IG feed video |

Or pick any exact size: `--to 8MB`, `--to 700kb`, `--to 1.5GB`.

### Install

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

### Usage

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

### Notes

- Output is always `.mp4` (H.264 + AAC, `yuv420p`, `+faststart`) — plays everywhere: phones, TVs, WhatsApp, browsers.
- Files already under target are skipped (never re-encoded bigger).
- Windows terminals get UTF-8 output automatically (no more `UnicodeEncodeError`).
- Speed: a 1-minute 1080p video takes ~10–20 s on a laptop CPU.

### FAQ

**Does it upload my video anywhere?** No. 100 % local, ffmpeg only.

**Can it get under 1 MB?** Yes — quality gets mushy but it fits. Audio drops to 32 kbps first.

**Where's the audio?** Kept (stereo AAC). Only dropped if the source has none.

---

## 🇹🇷 Türkçe

### Neden?

Her gün milyonlarca kişi aynı duvara çarpıyor: *"video göndermek için çok büyük"*.
Online dönüştürücüler özel videolarınızı **tanımadığınız sunuculara yüklemenizi** ister
(üstelik filigran basar). Video editörleri ise "bunu 16 MB altına sığdır" işi için
fazlasıyla gereksizdir.

`shrinkvid` tek bir iş yapar: **hedef boyuta tam oturmak** — mümkün olan en iyi
kaliteyle, tamamen çevrimdışı.

### Nasıl çalışır?

1. Gerçek süre ve ses bilgisi `ffmpeg` ile okunur (`ffprobe` gerekmez).
2. Boyut bütçesi video + ses bitrate'ine bölünür (ses kısılır, video kalitesini korur).
3. Sonuç hâlâ hedefi aşıyorsa otomatik olarak 720p → 480p → 360p → 240p ile yeniden
   denenir; sığana kadar.

### Hazır ayarlar

| Ayar | Hedef | Tipik kullanım |
|---|---|---|
| `--for whatsapp` | 16 MB | WhatsApp durum / mesaj |
| `--for discord` | 10 MB | Discord ücretsiz yükleme |
| `--for email` | 25 MB | E-posta eki |
| `--for instagram` | 60 MB | Instagram akış videosu |

İstediğiniz kesin boyutu da verebilirsiniz: `--to 8MB`, `--to 700kb`, `--to 1.5GB`.

### Kurulum

**1. Python 3.9+** ve **ffmpeg** (PATH'te olsun):

```bash
# Windows
winget install Gyan.FFmpeg
# macOS
brew install ffmpeg
# Linux
sudo apt install ffmpeg
```

**2. `shrinkvid.py` dosyasını indirin** — uygulamanın tamamı bu tek dosya:

```bash
curl -LO https://raw.githubusercontent.com/Volvox6767/shrinkvid/main/shrinkvid.py
```

`pip install` gerekmez. Tek dosya, sıfır bağımlılık.

### Kullanım

```
python shrinkvid.py GİRDİ... --to BOYUT | --for AYAR [--out DOSYA] [--overwrite] [--fast]

GİRDİ...         bir veya daha fazla video dosyası ve/veya klasör
--to BOYUT       kesin hedef, örn. 16MB, 700kb, 1.5GB
--for AYAR       whatsapp | discord | email | instagram
--out DOSYA      çıktı yolu (tek girdi için)
--overwrite      çıktı dosyası varsa üzerine yaz
--fast           daha az yedek çözünürlük (daha hızlı, genelde yeterli)
```

Desteklenen girdiler: `mp4 mov mkv avi webm m4v ts wmv flv`.

Örnekler:

```bash
python shrinkvid.py video.mp4 --for discord              # video_10mb.mp4
python shrinkvid.py a.mp4 b.mp4 --to 25MB                # toplu işlem
python shrinkvid.py ./kayitlar --to 8MB --overwrite      # tüm klasör
```

### Notlar

- Çıktı her zaman `.mp4` (H.264 + AAC, `yuv420p`, `+faststart`) — her yerde oynar: telefon, TV, WhatsApp, tarayıcı.
- Hedefin altında olan dosyalar atlanır (hiçbir dosya büyütülerek yeniden kodlanmaz).
- Windows terminalde çıktı otomatik UTF-8'dir (`UnicodeEncodeError` yaşamazsınız).
- Hız: 1 dakikalık 1080p video dizüstü CPU'sunda ~10–20 saniye.

### SSS

**Videoyu bir yere yüklüyor mu?** Hayır. %100 yerel, sadece ffmpeg.

**1 MB altına inebilir mi?** Evet — kalite bulanıklaşır ama sığar. Önce ses 32 kbps'e düşer.

**Ses ne oluyor?** Korunur (stereo AAC). Yalnızca kaynakta ses yoksa eklenmez.

---

Made with ❤ by **Ahmet Gedik** — [instagram.com/ahmetgedik67](https://www.instagram.com/ahmetgedik67)
Follow on Instagram for more free everyday tools.
Daha fazla ücretsiz günlük araç için Instagram'da takip edin.

License / Lisans: [MIT](LICENSE)
