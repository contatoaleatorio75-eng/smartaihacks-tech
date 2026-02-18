from moviepy import VideoFileClip, concatenate_videoclips
import os

def simple_concat():
    temp_dir = os.path.join("output", "temp_scenes")
    output_file = os.path.join("output", "O_Banquete_de_Cinzas_Shorts.mp4")
    
    files = sorted([os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith(".mp4")])
    
    if not files:
        print("Nenhuma cena encontrada.")
        return

    print(f"Concatenando {len(files)} cenas pre-renderizadas...")
    
    clips = [VideoFileClip(f) for f in files]
    
    # Use method="chain" which is much more memory efficient for simple concatenation
    final_video = concatenate_videoclips(clips, method="chain")
    
    final_video.write_videofile(
        output_file,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )
    
    print(f"Video finalizado: {output_file}")
    
    # Copiar para o Desktop
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    target_desktop = os.path.join(desktop, "O_Banquete_de_Cinzas_Shorts.mp4")
    
    # Usando shutil para cópia mais segura em Python
    import shutil
    shutil.copy2(output_file, target_desktop)
    print(f"Video copiado para o Desktop: {target_desktop}")

    # Close clips
    for c in clips:
        c.close()

if __name__ == "__main__":
    simple_concat()
