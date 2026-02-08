import os
import requests
import logging
from moviepy import VideoFileClip, TextClip, ColorClip, CompositeVideoClip, AudioFileClip, CompositeAudioClip
from moviepy.video.fx.MultiplySpeed import MultiplySpeed
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_elevenlabs_audio(text, output_file, api_key, voice_id):
    """
    Generate MP3 audio from text using ElevenLabs API.
    """
    if not text or not api_key:
        return False
        
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            return True
        else:
            logging.error(f"ElevenLabs API Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logging.error(f"ElevenLabs Request Failed: {e}")
        return False

def process_video(input_path, output_path, settings):
    """
    Process video with Speed, Audio Intro (ElevenLabs + Ducking), and Watermark (Box/Text).
    """
    try:
        logging.info(f"Processing video: {input_path}")
        clip = VideoFileClip(input_path)
        
        # --- Step 1: Speed ---
        speed_multiplier = settings.get("speed_multiplier", 1.05)
        if speed_multiplier != 1.0:
            logging.info(f"Applying Speed Multiplier: {speed_multiplier}x")
            clip = clip.with_effects([MultiplySpeed(factor=speed_multiplier)])
            
        # --- Step 2: Audio (The Intro) ---
        intro_script = settings.get("intro_script", "")
        use_elevenlabs = settings.get("use_elevenlabs", False)
        
        if use_elevenlabs and intro_script:
            logging.info("Generating ElevenLabs Intro Audio...")
            intro_audio_path = "temp_intro.mp3"
            api_key = settings.get("elevenlabs_key", "")
            voice_id = settings.get("elevenlabs_voice", "pNInz6obpgDQGcFmaJgB")
            
            success = generate_elevenlabs_audio(intro_script, intro_audio_path, api_key, voice_id)
            
            if success and os.path.exists(intro_audio_path):
                intro_audio = AudioFileClip(intro_audio_path)
                intro_duration = intro_audio.duration
                
                if intro_duration < clip.duration:
                    original_audio = clip.audio
                    
                    # Audio Ducking Logic
                    # 1. First part: Original Audio (Volume 20%) during intro
                    part1_ducked = original_audio.subclip(0, intro_duration).with_effects([MultiplyVolume(0.2)])
                    
                    # 2. Rest part: Original Audio (Volume 100%)
                    part2_normal = original_audio.subclip(intro_duration)
                    
                    # 3. Concatenate modified original audio
                    from moviepy.audio.AudioClip import CompositeAudioClip, concatenate_audioclips
                    background_audio = concatenate_audioclips([part1_ducked, part2_normal])
                    
                    # 4. Composite Intro + Background
                    final_audio = CompositeAudioClip([background_audio, intro_audio.set_start(0)])
                    clip.audio = final_audio
                    logging.info("Audio Ducking Applied.")
                else:
                    logging.warning("Intro audio is longer than video. Skipping ducking.")
                
                # Cleanup happens later or relies on temp file overwrite
            else:
                logging.warning("Failed to generate intro audio.")

        # --- Step 3: Watermark (The Layering) ---
        if settings.get("add_watermark", False):
            wm_text = settings.get("watermark_text", "My Channel")
            wm_style = settings.get("watermark_style", "Simple Text")
            opacity = settings.get("watermark_opacity", 0.8)
            
            # Position Calculation (Center of watermark)
            pos_x_percent = settings.get("watermark_x", 50)
            pos_y_percent = settings.get("watermark_y", 85)
            
            x_px = clip.w * (pos_x_percent / 100)
            y_px = clip.h * (pos_y_percent / 100)
            
            logging.info(f"Adding Watermark: '{wm_text}' at ({x_px}, {y_px})")
            
            try:
                # Create TextClip
                # Note: 'method="label"' is often safer for ImageMagick/MoviePy compatibility
                txt_clip = TextClip(
                    text=wm_text, 
                    font_size=50, 
                    color='white', 
                    font='Arial-Bold', 
                    stroke_color='black', 
                    stroke_width=2,
                    method='label'
                )
                txt_clip = txt_clip.set_duration(clip.duration).set_opacity(opacity)
                
                layers = [clip]
                
                # The "Box" Logic
                if "Box" in wm_style:
                    w, h = txt_clip.size
                    box_w = w + 40
                    box_h = h + 20
                    
                    box_opacity = 0.6 if "Transparent" in wm_style else 1.0
                    
                    # Create Black Box
                    box_clip = ColorClip(size=(box_w, box_h), color=(0,0,0))
                    box_clip = box_clip.set_opacity(box_opacity).set_duration(clip.duration)
                    
                    # Position Box centered at x_px, y_px
                    box_clip = box_clip.set_position(lambda t: (x_px - box_w/2, y_px - box_h/2))
                    layers.append(box_clip)
                    
                    # Position Text centered at x_px, y_px (which means centered on box)
                    txt_clip = txt_clip.set_position(lambda t: (x_px - w/2, y_px - h/2))
                    layers.append(txt_clip)
                else:
                    # Simple Text Positioning
                    w, h = txt_clip.size
                    txt_clip = txt_clip.set_position(lambda t: (x_px - w/2, y_px - h/2))
                    layers.append(txt_clip)
                
                # Compositing
                clip = CompositeVideoClip(layers)
                
            except Exception as e:
                logging.error(f"Watermark Error: {e}")

        # --- Step 4: Output ---
        logging.info(f"Writing output to {output_path}...")
        clip.write_videofile(
            output_path, 
            codec='libx264', 
            audio_codec='aac', 
            fps=30, 
            preset='ultrafast',
            logger=None
        )
        
        # Cleanup resources
        clip.close()
        return True

    except Exception as e:
        logging.error(f"Processing Failed: {e}")
        return False
