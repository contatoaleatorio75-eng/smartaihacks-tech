import os
import json
import numpy as np
import textwrap
import sys
import io
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
import moviepy.video.fx as vfx

# Forçar UTF-8 para evitar erros de encoding no terminal Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def create_subtitle_clip(text, video_size, duration):
    """Gera um clipe de legenda discreto para YouTube Shorts (9:16)."""
    width, height = video_size
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Fonte maior para Shorts
    font_size = 50
    try:
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        font = ImageFont.load_default()
            
    # Quebra de linha mais agressiva para o formato vertical
    wrapper = textwrap.TextWrapper(width=30) 
    wrapped_text = "\n".join(wrapper.wrap(text))
    
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    x = (width - tw) / 2
    # Posição: Centro-inferior, bem visível
    y = (height * 0.75) - (th / 2) 
    
    padding_x, padding_y = 30, 15
    draw.rectangle(
        [x - padding_x, y - padding_y, x + tw + padding_x, y + th + padding_y],
        fill=(0, 0, 0, 180) 
    )
    
    draw.multiline_text((x, y), wrapped_text, font=font, fill=(255, 255, 255, 255), align="center")
    
    img_array = np.array(img)
    return ImageClip(img_array).with_duration(duration)

def apply_ken_burns(clip, duration, zoom_ratio=0.10):
    """Aplica um efeito de zoom suave em ImageClips."""
    return clip.resized(lambda t: 1.0 + zoom_ratio * (t / duration)).with_duration(duration)

def create_cta_overlay(text, video_size, duration):
    """Gera um banner de CTA chamativo para Shorts."""
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
    
    x = (width - tw) / 2
    y = 150 # Topo para Shorts
    
    padding_x, padding_y = 40, 20
    draw.rectangle(
        [x - padding_x, y - padding_y, x + tw + padding_x, y + th + padding_y],
        fill=(220, 20, 60, 220) # Crimson Red
    )
    draw.multiline_text((x, y), wrapped_text, font=font, fill=(255, 255, 255, 255), align="center")
    
    img_array = np.array(img)
    return ImageClip(img_array).with_duration(duration)

def assemble_video():
    scenes_path = os.path.join("output", "scenes.json")
    audio_dir = os.path.join("output", "audio")
    assets_dir = os.path.join("output", "assets")
    temp_dir = os.path.join("output", "temp_scenes")
    output_file = os.path.join("output", "Beyond_GPT5_Documentary.mp4")

    os.makedirs(temp_dir, exist_ok=True)

    if not os.path.exists(scenes_path):
        print("❌ scenes.json não encontrado.")
        return

    with open(scenes_path, "r", encoding="utf-8") as f:
        scenes = json.load(f).get("scenes", [])

    target_w, target_h = 1080, 1920
    temp_files = []

    print(f"Iniciando montagem robusta HD ({len(scenes)} cenas)...")

    for i, scene in enumerate(scenes):
        audio_path = os.path.join(audio_dir, f"scene_{i:03d}.mp3")
        video_path = os.path.join(assets_dir, f"scene_{i:03d}.mp4")
        image_path = os.path.join(assets_dir, f"scene_{i:03d}.jpg")
        temp_scene_path = os.path.join(temp_dir, f"scene_{i:03d}.mp4")
        
        # Pular se o áudio não existir ou estiver vazio (0 bytes)
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            continue

        if os.path.exists(temp_scene_path):
            print(f"Cena {i} ja renderizada. Pulando.")
            temp_files.append(temp_scene_path)
            continue

        print(f"Renderizando Cena {i}/{len(scenes)-1}...")
            
        try:
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # Carregar Mídia
            if os.path.exists(video_path):
                main_clip = VideoFileClip(video_path).without_audio()
                if main_clip.duration < duration:
                    main_clip = vfx.Loop(duration=duration).apply(main_clip)
                else:
                    main_clip = main_clip.with_duration(duration)
            elif os.path.exists(image_path):
                main_clip = ImageClip(image_path).with_duration(duration)
                main_clip = apply_ken_burns(main_clip, duration)
            else:
                continue

            # Redimensionamento Fixo
            main_clip = main_clip.resized(height=target_h)
            if main_clip.w < target_w:
                main_clip = main_clip.resized(width=target_w)
                
            main_clip = main_clip.cropped(
                x1=max(0, main_clip.w/2 - target_w/2),
                y1=max(0, main_clip.h/2 - target_h/2),
                width=target_w,
                height=target_h
            )

            main_clip = main_clip.with_audio(audio_clip)
            
            # Overlays
            overlay_elements = [main_clip]
            text = scene.get("text", "")
            if text:
                overlay_elements.append(create_subtitle_clip(text, (target_w, target_h), duration))
            
            # CTA Inicial (Cena 0)
            if i == 0:
                overlay_elements.append(create_cta_overlay("INSCREVA-SE NO CANAL ALÊATÓRIO!", (target_w, target_h), duration))
            
            # CTA Final (Última Cena)
            if i == len(scenes) - 1:
                overlay_elements.append(create_cta_overlay("CURTA, COMENTE E ATIVE O SININHO!\nCANAL ALÊATÓRIO", (target_w, target_h), duration))

            final_scene = CompositeVideoClip(overlay_elements)
            
            # Renderizar apenas esta cena
            final_scene.write_videofile(
                temp_scene_path, 
                fps=24, 
                codec="libx264", 
                audio_codec="aac",
                logger=None # Silencioso para não poluir o terminal
            )
            temp_files.append(temp_scene_path)
            
            # Fechar clips para liberar memória AGRESSIVAMENTE
            final_scene.close()
            audio_clip.close()
            main_clip.close()

        except Exception as e:
            print(f"❌ Erro na cena {i}: {e}")

    if temp_files:
        print(f"✅ {len(temp_files)} scenes rendered to {temp_dir}. Use stitch_video.py for final merge.")
    else:
        print("❌ Nenhum clipe processado com sucesso.")

if __name__ == "__main__":
    assemble_video()

if __name__ == "__main__":
    assemble_video()
