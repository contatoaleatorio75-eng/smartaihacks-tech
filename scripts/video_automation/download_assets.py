import os
import json
import requests
from config import PEXELS_API_KEY

def download_assets():
    if not PEXELS_API_KEY:
        print("❌ PEXELS_API_KEY não encontrada.")
        return

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

    for i, scene in enumerate(scenes):
        query = scene.get("search_query")
        if not query:
            continue
            
        # Assets can be .mp4 or .jpg
        video_path = f"scene_{i:03d}.mp4"
        image_path = f"scene_{i:03d}.jpg"
        
        if os.path.exists(os.path.join(output_dir, video_path)) or os.path.exists(os.path.join(output_dir, image_path)):
            print(f"⏩ Asset {i} já existe.")
            continue

        print(f"🔍 Buscando mídia para Cena {i}: '{query}'...")
        
        # 1. Tentar VÍDEO (Landscape)
        url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=landscape"
        
        try:
            response = requests.get(url, headers=headers)
            res_data = response.json()
            videos = res_data.get("videos", [])
            
            if videos:
                video_files = videos[0].get("video_files", [])
                # Melhor qualidade MP4
                download_url = None
                for vf in sorted(video_files, key=lambda x: x.get("width", 0), reverse=True):
                    if vf.get("file_type") == "video/mp4":
                        download_url = vf.get("link")
                        break
                
                if download_url:
                    print(f"⬇️ Baixando VÍDEO para Cena {i}...")
                    v_res = requests.get(download_url)
                    with open(os.path.join(output_dir, video_path), "wb") as f:
                        f.write(v_res.content)
                    print(f"✅ Vídeo salvo: {video_path}")
                    continue

        except Exception as e:
            print(f"⚠️ Erro ao buscar vídeo {i}: {e}")

        # 2. Fallback para IMAGEM (Landscape)
        print(f"🖼️ Fallback para IMAGEM na Cena {i}...")
        img_url = f"https://api.pexels.com/v1/search?query={query}&per_page=1&orientation=landscape"
        
        try:
            response = requests.get(img_url, headers=headers)
            res_data = response.json()
            photos = res_data.get("photos", [])
            
            if photos:
                download_url = photos[0].get("src", {}).get("large2x")
                if download_url:
                    print(f"⬇️ Baixando IMAGEM para Cena {i}...")
                    img_res = requests.get(download_url)
                    with open(os.path.join(output_dir, image_path), "wb") as f:
                        f.write(img_res.content)
                    print(f"✅ Imagem salva: {image_path}")
                else:
                    print(f"⚠️ Link de imagem não encontrado para Cena {i}.")
            else:
                print(f"❌ Nenhuma mídia encontrada para '{query}'.")

        except Exception as e:
            print(f"❌ Erro ao buscar imagem {i}: {e}")

if __name__ == "__main__":
    download_assets()
