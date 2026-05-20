import streamlit as st
import os
import yt_dlp
from bot import process_video
# from openai import OpenAI # Commented out as key handling is sensitive, keeping import structure

# --- CONFIG ---
st.set_page_config(page_title="Ghost Bot Pro", layout="wide")

# Initialize Session State (To remember data after reload)
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'ai_title' not in st.session_state:
    st.session_state.ai_title = ""
if 'ai_desc' not in st.session_state:
    st.session_state.ai_desc = ""

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Ghost Settings")
    
    st.subheader("1. Source")
    url = st.text_input("Video URL (YT/Insta)")
    
    st.subheader("2. Edits")
    speed = st.slider("Speed", 1.0, 1.5, 1.05)
    
    st.subheader("3. Audio (ElevenLabs)")
    use_eleven = st.checkbox("Use AI Intro")
    eleven_key = ""
    voice_id = "21m00Tcm4TlvDq8ikWAM"
    intro_script = ""
    
    if use_eleven:
        eleven_key = st.text_input("ElevenLabs Key", type="password")
        voice_id = st.text_input("Voice ID", value="21m00Tcm4TlvDq8ikWAM")
        st.caption("Common IDs: Adam (pNInz...), Antoni (ErXwo...), Rachel (21m00...)")
        intro_script = st.text_area("Intro Script")

    st.subheader("4. Watermark")
    add_watermark = st.checkbox("Add Watermark")
    wm_text = "@MyChannel"
    wm_style = "Simple Text"
    wm_x = 50
    wm_y = 85
    
    if add_watermark:
        wm_text = st.text_input("Watermark Text", value="@MyChannel")
        wm_style = st.selectbox("Style", ["Simple Text", "Black Box (Solid)", "Transparent Box"])
        wm_x = st.slider("X Position (%)", 0, 100, 50)
        wm_y = st.slider("Y Position (%)", 0, 100, 85)

# --- MAIN APP ---
st.title("🤖 Ghost Bot Pro (Nuclear Edition)")

if st.button("Process Video", type="primary"):
    if not url:
        st.error("Please enter a URL!")
    else:
        with st.status("Processing...", expanded=True) as status:
            st.write("📥 Downloading...")
            
            # Cleanup
            if os.path.exists("temp_raw.mp4"): os.remove("temp_raw.mp4")
            if os.path.exists("temp_final.mp4"): os.remove("temp_final.mp4")
            
            # Download
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': 'temp_raw.%(ext)s',
                'quiet': True,
                'overwrites': True
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # Find file
                input_file = None
                for f in os.listdir("."):
                    if f.startswith("temp_raw"):
                        input_file = f
                        break
                
                if input_file:
                    st.write("⚙️ Editing (Speed, Audio, Watermark)...")
                    
                    settings = {
                        "speed_multiplier": speed,
                        "use_elevenlabs": use_eleven,
                        "elevenlabs_key": eleven_key,
                        "elevenlabs_voice": voice_id,
                        "intro_script": intro_script,
                        "add_watermark": add_watermark,
                        "watermark_text": wm_text,
                        "watermark_style": wm_style,
                        "watermark_x": wm_x,
                        "watermark_y": wm_y
                    }
                    
                    success = process_video(input_file, "temp_final.mp4", settings)
                    
                    if success:
                        st.session_state.processed = True
                        status.update(label="Complete!", state="complete")
                    else:
                        st.error("Processing Failed")
                        status.update(label="Failed", state="error")
                else:
                    st.error("Download Failed")
                    status.update(label="Failed", state="error")
                    
            except Exception as e:
                st.error(f"Error: {e}")
                status.update(label="Error", state="error")

# Display Result (Using Session State so it persists)
if st.session_state.processed:
    st.success("Video Ready!")
    if os.path.exists("temp_final.mp4"):
        st.video("temp_final.mp4")
    
    # Optional: AI Title/Desc generation could go here using st.session_state.ai_title
    # But sticking to core video processing for now as per instructions.
