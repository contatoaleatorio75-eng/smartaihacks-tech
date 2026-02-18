import os
import json
import requests
from config import PEXELS_API_KEY

def download_images():
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

    output_dir = os.path.join("output", "images")
    os.makedirs(output_dir, exist_ok=True)

    headers = {"Authorization": PEXELS_API_KEY}

    for i, scene in enumerate(scenes):
        query = scene.get("search_query")
        if not query:
            continue
            
        filename = f"scene_{i:03d}.jpg"
        output_path = os.path.join(output_dir, filename)
        
        if os.path.exists(output_path):
            print(f"⏩ Imagem {i} já existe: {filename}")
            continue

        print(f"🔍 Buscando imagem para Cena {i}: '{query}'...")
        
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
        
        try:
            response = requests.get(url, headers=headers)
            res_data = response.json()
            
            photos = res_data.get("photos", [])
            if not photos:
                print(f"⚠️ Nenhuma imagem encontrada para '{query}'.")
                continue
                
            # Pegar a versão 'large2x' para garantir boa resolução para o Shorts
            download_url = photos[0].get("src", {}).get("large2x")
            
            if not download_url:
                print(f"⚠️ Link de download não encontrado para Cena {i}.")
                continue

            print(f"⬇️ Baixando Imagem {i}...")
            r = requests.get(download_url)
            with open(output_path, "wb") as f:
                f.write(r.content)
            print(f"✅ Salvo: {filename}")

        except Exception as e:
            print(f"❌ Erro ao baixar imagem {i}: {e}")

if __name__ == "__main__":
    download_images()
