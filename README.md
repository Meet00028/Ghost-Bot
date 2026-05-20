# 🤖 Ghost Bot Pro (Nuclear Edition)

Ghost Bot Pro is a powerful automated video processing tool built with Python, Streamlit, and MoviePy. It allows you to download videos from YouTube or Instagram, apply custom edits like speed adjustments, add AI-generated audio intros using ElevenLabs, and overlay watermarks.

## 🚀 Features

- **Video Downloader**: Download videos directly from YouTube and Instagram URLs using `yt-dlp`.
- **Speed Adjustment**: Increase video speed (1.0x to 1.5x) with high-quality audio preservation.
- **AI Audio Intro**: Generate professional AI voiceovers using **ElevenLabs** and composite them into the video with automatic audio ducking.
- **Custom Watermarks**: Add text watermarks with various styles:
  - Simple Text
  - Solid Black Box
  - Transparent Box
- **Streamlit UI**: A clean, intuitive dashboard for managing settings and processing videos in real-time.

## 🛠️ Installation

Ensure you have Python 3.8+ installed on your system.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Meet00028/Ghost-Bot.git
   cd "Ghost Bot"
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install ImageMagick** (Required for MoviePy TextClips):
   - **macOS**: `brew install imagemagick`
   - **Linux**: `sudo apt install imagemagick`
   - **Windows**: Download from [ImageMagick website](https://imagemagick.org/script/download.php).

## 🚦 How to Run

To start the Ghost Bot Pro web interface, run:

```bash
source venv/bin/activate
streamlit run app.py
```

## ⚙️ Configuration

- **ElevenLabs**: You will need an ElevenLabs API key if you want to use the AI Intro feature.
- **Watermarks**: You can customize the text, style, and position (X/Y) directly from the sidebar.

## 📦 Dependencies

- `streamlit`: Web interface
- `moviepy`: Video editing and compositing
- `yt-dlp`: Video downloading
- `elevenlabs`: AI voice generation
- `requests`: API handling

---
Developed by [Meet00028](https://github.com/Meet00028)
