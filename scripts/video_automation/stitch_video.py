import os
import subprocess

def concatenate_scenes_ffmpeg():
    temp_dir = os.path.join("output", "temp_scenes")
    output_file = os.path.join("output", "O_Banquete_de_Cinzas_Shorts.mp4")
    list_file = "scenes_list.txt"

    if not os.path.exists(temp_dir):
        print(f"❌ Diretório {temp_dir} não encontrado.")
        return

    # Obter todos os arquivos mp4 ordenados numericamente
    files = sorted([f for f in os.listdir(temp_dir) if f.endswith(".mp4")])
    
    if not files:
        print("❌ Nenhuma cena encontrada para concatenar.")
        return

    # Escrever a lista para o ffmpeg
    with open(list_file, "w") as f:
        for filename in files:
            path = os.path.abspath(os.path.join(temp_dir, filename))
            f.write(f"file '{path}'\n")

    print(f"🎞️ Concatenando {len(files)} cenas via FFMPEG...")
    
    # Comando ffmpeg concat demuxer
    command = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", 
        "-i", list_file, 
        "-c", "copy", 
        output_file
    ]

    try:
        subprocess.run(command, check=True)
        print(f"✅ Vídeo finalizado com FFMPEG: {output_file}")
        # Copiar para o Desktop
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        target_desktop = os.path.join(desktop, "O_Banquete_de_Cinzas_Shorts.mp4")
        subprocess.run(["copy", output_file, target_desktop], shell=True)
        print(f"🚀 Vídeo copiado para o Desktop: {target_desktop}")

    except Exception as e:
        print(f"❌ Erro ao concatenar com FFMPEG: {e}")
    finally:
        if os.path.exists(list_file):
            os.remove(list_file)

if __name__ == "__main__":
    concatenate_scenes_ffmpeg()
