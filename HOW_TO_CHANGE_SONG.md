# 🎵 How to Change Your Daily Portfolio Song

This guide explains how to update the song that plays when clicking the headphones in your interactive portfolio.

---

## 📍 Where Can You Run This From? (Any Terminal Anywhere!)

* **You do NOT need to be in this project directory.** You do NOT need to `cd` anywhere.
* Just press `Ctrl + Alt + T` (or open any terminal prompt from your Desktop, Home folder, etc.) and run:
  ```bash
  changesong "https://youtu.be/..."
  ```
* Because `changesong` is linked into your system PATH (`~/.local/bin/changesong`), it is available **globally** in every terminal session.
* Wherever you run it from, it automatically locates the portfolio, updates your local file, and pushes the change to your live website Gist.

---

## 🔗 Supported Link Formats

The tool automatically detects and formats all common music and video links:

| Source | Example Format |
|---|---|
| **Standard YouTube** | `changesong "https://www.youtube.com/watch?v=wok0OoivstE"` |
| **YouTube Short Link** | `changesong "https://youtu.be/wok0OoivstE"` |
| **YouTube Music** | `changesong "https://music.youtube.com/watch?v=wok0OoivstE"` |
| **YouTube Shorts** | `changesong "https://www.youtube.com/shorts/wok0OoivstE"` |
| **Plain Video ID** | `changesong wok0OoivstE` |
| **Direct MP3 / Audio** | `changesong "https://example.com/music/lofi-track.mp3"` |

> **Tip:** Always enclose links with quotes `" "` to avoid shell character issues with `?` or `&`.

---

## 🔍 How to Check the Current Song

Run the command without any arguments:

```bash
changesong
```

**Output example:**
```text
🎧 Current Song:
   • Type: youtube
   • ID: wok0OoivstE
   • URL: https://www.youtube-nocookie.com/embed/wok0OoivstE?autoplay=1&loop=1&playlist=wok0OoivstE
   • Last updated: 2026-09-14T01:06:31Z
   • Live Gist: https://gist.github.com/aDNAn-itis/75717a69797a2327cefec3e8c68906eb
```

---

## ☁️ How It Works (Zero-Commit Cloud Sync)

To keep your Git repository history clean and prevent 30+ clutter commits every month:

1. **GitHub Gist**: The active song is stored in a dedicated public Gist on your account:  
   👉 [https://gist.github.com/aDNAn-itis/75717a69797a2327cefec3e8c68906eb](https://gist.github.com/aDNAn-itis/75717a69797a2327cefec3e8c68906eb)
2. **Instant Sync**: When you run `changesong <url>`, it updates the Gist in ~1 second using your authenticated `gh` CLI.
3. **Live Update**: When visitors open your website, it automatically fetches the latest song from the Gist.
4. **Local Fallback**: It also updates your local `song.js` so everything works seamlessly offline.
5. **Git History**: **0 commits are added to your repository**, ever!
