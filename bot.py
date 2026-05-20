import os
import requests
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip, AudioFileClip, CompositeAudioClip, vfx

def generate_elevenlabs_audio(text, voice_id, api_key, output_path):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            print(f"ElevenLabs Error: {response.text}")
            return False
    except Exception as e:
        print(f"ElevenLabs Request Failed: {e}")
        return False

def process_video(input_path, output_path, settings):
    print(f"🎬 PROCESSING: {input_path}")
    
    # 1. Load Video
    video = VideoFileClip(input_path)
    
    # 2. Apply Speed (CRITICAL: Reassign variable)
    speed = settings.get('speed_multiplier', 1.05)
    video = video.fx(vfx.speedx, speed)
    
    # 3. Handle Audio Intro (Audio Ducking)
    if settings.get('use_elevenlabs') and settings.get('intro_script'):
        print("   - Generating AI Audio...")
        audio_path = "temp_intro.mp3"
        # Ensure we have a voice ID and Key, otherwise skip or fallback
        api_key = settings.get('elevenlabs_key')
        voice_id = settings.get('elevenlabs_voice', '21m00Tcm4TlvDq8ikWAM')
        
        if api_key:
            success = generate_elevenlabs_audio(
                settings['intro_script'], 
                voice_id, 
                api_key, 
                audio_path
            )
            
            if success and os.path.exists(audio_path):
                intro_audio = AudioFileClip(audio_path)
                # Ducking: Lower original volume to 10%
                original_audio = video.audio.volumex(0.1)
                
                # Combine: Intro at 100% vol, Original at 10% vol
                # We set intro start at 0
                final_audio = CompositeAudioClip([original_audio, intro_audio.set_start(0)])
                video = video.set_audio(final_audio)
    
    # 4. Handle Watermark (Layering)
    final_layers = [video] # Layer 0 is video
    
    if settings.get('add_watermark'):
        text = settings.get('watermark_text', '@MyChannel')
        
        # Calculate Position Pixels
        pos_x = settings.get('watermark_x', 50) / 100 * video.w
        pos_y = settings.get('watermark_y', 85) / 100 * video.h
        
        # Create Text Clip
        # Note: MoviePy TextClip requires ImageMagick. If not installed, this might fail.
        # Ensure 'transparent' background is handled if needed, but TextClip usually has transparent bg by default.
        txt_clip = TextClip(text, fontsize=60, color='white', font='Arial-Bold', stroke_color='black', stroke_width=2)
        txt_clip = txt_clip.set_position('center').set_duration(video.duration)
        
        # Create Background Box (The "Cover Up" Layer)
        wm_style = settings.get('watermark_style', 'Simple Text')
        if "Box" in wm_style:
            box_w = txt_clip.w + 50
            box_h = txt_clip.h + 30
            opacity = 0.6 if "Transparent" in wm_style else 1.0
            
            box = ColorClip(size=(int(box_w), int(box_h)), color=(0,0,0))
            box = box.set_opacity(opacity).set_duration(video.duration)
            # Center box at the target X/Y
            # The target X/Y is the CENTER of the element
            box = box.set_position((pos_x - box_w/2, pos_y - box_h/2))
            
            final_layers.append(box) # Add Box First
        
        # Set Text Position
        txt_clip = txt_clip.set_position((pos_x - txt_clip.w/2, pos_y - txt_clip.h/2))
        final_layers.append(txt_clip) # Add Text Last
    
    # 5. Composite Final Video
    final_video = CompositeVideoClip(final_layers)
    
    # 6. Render
    # Using 'libx264' and 'aac' for best compatibility
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=30)
    return True
