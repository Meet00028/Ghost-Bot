import streamlit as st
import os
import yt_dlp
from bot import process_video

st.set_page_config(page_title="YouTube Automation Bot", layout="wide")
st.title("🤖 YouTube Automation Bot (Pro Version)")

# --- Sidebar Organization ---
st.sidebar.header("Configuration")

# Section 1: Source
st.sidebar.subheader("1. Source Video")
video_url = st.sidebar.text_input("YouTube/Instagram URL")

# Section 2: Speed
st.sidebar.subheader("2. Speed")
speed_multiplier = st.sidebar.slider("Speed Multiplier", 0.5, 2.0, 1.05, 0.05)

# Section 3: Audio (ElevenLabs)
st.sidebar.subheader("3. Audio (ElevenLabs)")
use_elevenlabs = st.sidebar.checkbox("Use ElevenLabs Intro")
elevenlabs_key = ""
elevenlabs_voice = ""
intro_script = ""

if use_elevenlabs:
    elevenlabs_key = st.sidebar.text_input("API Key", type="password")
    elevenlabs_voice = st.sidebar.text_input("Voice ID", value="pNInz6obpgDQGcFmaJgB") # Default Adam
    intro_script = st.sidebar.text_area("Intro Script (Leave empty to skip audio)")

# Section 4: Watermark (The Overlay)
st.sidebar.subheader("4. Watermark")
add_watermark = st.sidebar.checkbox("Add Watermark")
wm_text = ""
wm_style = "Simple Text"
wm_x = 50
wm_y = 85
wm_opacity = 0.8

if add_watermark:
    wm_text = st.sidebar.text_input("Watermark Text", value="@MyChannel")
    wm_style = st.sidebar.selectbox("Style", ["Simple Text", "Black Box (Solid)", "Transparent Box"])
    wm_x = st.sidebar.slider("Position X (%)", 0, 100, 50)
    wm_y = st.sidebar.slider("Position Y (%)", 0, 100, 85)
    wm_opacity = st.sidebar.slider("Opacity", 0.1, 1.0, 0.8)

# --- Main Logic ---
if st.button("Process Video", type="primary"):
    if not video_url:
        st.error("Please enter a video URL first!")
    else:
        with st.status("Processing Video...", expanded=True) as status:
            # 1. Download Video
            st.write("📥 Downloading video...")
            temp_raw = "temp_raw.mp4"
            temp_final = "temp_final.mp4"
            
            # Clean up previous runs
            if os.path.exists(temp_raw): os.remove(temp_raw)
            if os.path.exists(temp_final): os.remove(temp_final)
            
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': 'temp_raw.%(ext)s',
                'quiet': True,
                'overwrites': True
            }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                
                # Check if download succeeded (handling potential extension differences)
                # Since we forced outtmpl, it might be temp_raw.mp4 or temp_raw.mkv etc.
                # Let's find the file starting with temp_raw
                downloaded_file = None
                for file in os.listdir("."):
                    if file.startswith("temp_raw"):
                        downloaded_file = file
                        break
                
                if not downloaded_file:
                    st.error("Download failed.")
                    status.update(label="Failed", state="error")
                else:
                    st.write("✅ Download Complete.")
                    
                    # 2. Prepare Settings
                    settings = {
                        "speed_multiplier": speed_multiplier,
                        "use_elevenlabs": use_elevenlabs,
                        "elevenlabs_key": elevenlabs_key,
                        "elevenlabs_voice": elevenlabs_voice,
                        "intro_script": intro_script,
                        "add_watermark": add_watermark,
                        "watermark_text": wm_text,
                        "watermark_style": wm_style,
                        "watermark_x": wm_x,
                        "watermark_y": wm_y,
                        "watermark_opacity": wm_opacity
                    }
                    
                    # 3. Process Video
                    st.write("⚙️ Processing video (Speed, Audio, Watermark)...")
                    success = process_video(downloaded_file, temp_final, settings)
                    
                    if success and os.path.exists(temp_final):
                        st.write("✅ Processing Complete!")
                        status.update(label="Done!", state="complete")
                        
                        # 4. Display Result
                        st.success("Your video is ready!")
                        st.video(temp_final)
                    else:
                        st.error("Processing failed during edit.")
                        status.update(label="Failed", state="error")
                        
            except Exception as e:
                st.error(f"An error occurred: {e}")
                status.update(label="Error", state="error")
