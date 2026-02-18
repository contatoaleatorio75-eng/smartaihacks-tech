import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import textwrap
import sys
import io
from moviepy import ImageClip, VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
import moviepy.video.fx as vfx

# Forçar UTF-8 para evitar erros de encoding no terminal Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def create_subtitle_clip(text, video_size, duration):
    width, height = video_size
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_size = 50
    try:
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        font = ImageFont.load_default()
    wrapper = textwrap.TextWrapper(width=30) 
    wrapped_text = "\n".join(wrapper.wrap(text))
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (width - tw) / 2
    y = (height * 0.75) - (th / 2) 
    padding_x, padding_y = 30, 15
    draw.rectangle([x - padding_x, y - padding_y, x + tw + padding_x, y + th + padding_y], fill=(0, 0, 0, 180))
    draw.multiline_text((x, y), wrapped_text, font=font, fill=(255, 255, 255, 255), align="center")
    return ImageClip(np.array(img)).with_duration(duration)

def create_cta_overlay(text, video_size, duration):
    width, height = video_size
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_size = 60
    try:
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        font = ImageFont.load_default()
    wrapper = textwrap.TextWrapper(width=20)
    wrapped_text = "\n".join(wrapper.wrap(text))
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = (width - tw) / 2, 150
    padding_x, padding_y = 40, 20
    draw.rectangle([x - padding_x, y - padding_y, x + tw + padding_x, y + th + padding_y], fill=(220, 20, 60, 220))
    draw.multiline_text((x, y), wrapped_text, font=font, fill=(255, 255, 255, 255), align="center")
    return ImageClip(np.array(img)).with_duration(duration)

def test_scene_11():
    audio_path = os.path.join("output", "audio", "scene_011.mp3")
    image_path = os.path.join("output", "assets", "scene_010.jpg")
    output_path = os.path.join("output", "temp_scenes", "scene_011.mp4")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    audio_clip = AudioFileClip(audio_path)
    main_clip = ImageClip(image_path).with_duration(audio_clip.duration).resized(height=1920)
    if main_clip.w < 1080: main_clip = main_clip.resized(width=1080)
    main_clip = main_clip.cropped(x1=main_clip.w/2 - 540, y1=main_clip.h/2 - 960, width=1080, height=1920).with_audio(audio_clip)
    
    sub = create_subtitle_clip("Se você gostou, deixe seu like, se inscreva no canal AlêAtório e ative o sininho! Até o próximo vídeo.", (1080, 1920), audio_clip.duration)
    cta = create_cta_overlay("CURTA, COMENTE E ATIVE O SININHO!\nCANAL ALÊATÓRIO", (1080, 1920), audio_clip.duration)
    
    final = CompositeVideoClip([main_clip, sub, cta])
    final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
    print("Done")

if __name__ == "__main__":
    test_scene_11()
