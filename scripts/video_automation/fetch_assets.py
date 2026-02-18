import os
import json
import requests
from config import PEXELS_API_KEY

def fetch_assets():
    # 1. Config
    if not PEXELS_API_KEY:
        print("❌ PEXELS_API_KEY não encontrada.")
        return

    # 2. Ler scenes.json
    scenes_path = os.path.join("output", "scenes.json")
    if not os.path.exists(scenes_path):
        print("❌ scenes.json não encontrado.")
        return

    with open(scenes_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        scenes = data.get("scenes", [])

    output_dir = os.path.join("output", "assets")
    os.makedirs(output_dir, exist_ok=True)

    headers = {"Authorization": PEXELS_API_KEY}

    # 3. Buscar e baixar assets
    for i, scene in enumerate(scenes):
        query = scene.get("search_query")
        if not query:
            continue

        filename = f"scene_{i:03d}.mp4"
        filepath = os.path.join(output_dir, filename)

        if os.path.exists(filepath):
            print(f"⏩ Asset {i} já existe: {filename}")
            continue

        print(f"🔍 Buscando vídeo para Cena {i}: '{query}'...")
        
        # Search API
        url = "https://api.pexels.com/videos/search"
        params = {
            "query": query,
            "per_page": 1,
            "orientation": "landscape", # ou "portrait"
            "size": "medium" # ou large/small
        }

        try:
            resp = requests.get(url, headers=headers, params=params)
            resp.raise_for_status()
            results = resp.json()
            
            videos = results.get("videos", [])
            if not videos:
                print(f"⚠️ Nenhum vídeo encontrado para '{query}'.")
                # TODO: Fallback ou ignorar
                continue

            # Escolher o melhor arquivo de vídeo (HD, sem marca d'água ideally)
            video_files = videos[0].get("video_files", [])
            
            # Preferir HD (1280x720) ou SD se não tiver
            # Sort by quality/width
            video_files.sort(key=lambda x: x.get("width", 0), reverse=True)
            
            # Try to pick one that is mp4
            best_video = None
            for vf in video_files:
                if vf.get("file_type") == "video/mp4":
                    best_video = vf
                    # Stop if we found a decent HD one (around 1920 or 1280)
                    if vf.get("width", 0) <= 1920:
                         break
            
            if not best_video:
                 best_video = video_files[0]

            download_link = best_video.get("link")
            print(f"⬇️ Baixando: {download_link}...")
            
            # Download content
            vid_resp = requests.get(download_link, stream=True)
            vid_resp.raise_for_status()
            
            with open(filepath, "wb") as f:
                for chunk in vid_resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ Salvo: {filename}")

        except Exception as e:
            print(f"❌ Erro ao buscar/baixar asset para cena {i}: {e}")

if __name__ == "__main__":
    fetch_assets()
