import os
import json
import base64
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

def generate_script():
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY não configurada.")
        return

    client = genai.Client(api_key=GEMINI_API_KEY)

    scenes_path = os.path.join("output", "scenes.json")
    assets_dir = os.path.join("output", "assets")
    
    if not os.path.exists(scenes_path):
        print("❌ scenes.json não encontrado.")
        return

    with open(scenes_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        scenes = data.get("scenes", [])

    print(f"Gerando roteiro narrativo para {len(scenes)} cenas...")
    
    new_scenes = []
    
    for i, scene in enumerate(scenes):
        print(f"Processando cena {i}: '{scene['text']}'")
        # Pular CTAs (primeiro e último)
        if i == 0 or i == len(scenes) - 1:
            new_scenes.append(scene)
            continue

        # Só gerar para as cenas que têm o placeholder "Cena X"
        if not scene["text"].startswith("Cena"):
            new_scenes.append(scene)
            continue

        image_path = os.path.join(assets_dir, scene["image"])
        if not os.path.exists(image_path):
            new_scenes.append(scene)
            continue

        print(f"Analisando imagem {scene['image']}...")
        
        with open(image_path, "rb") as f:
            image_data = f.read()
            
        try:
            # Usando a nova API do SDK google.genai com o formato de imagem correto
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=[
                    "Descreva o que está acontecendo nesta cena de um storyboard chamado 'O Banquete de Cinzas'. Escreva um parágrafo curto de narração (em português) que seja dramático e envolvente para um YouTube Short.",
                    types.Part.from_bytes(data=image_data, mime_type="image/jpeg")
                ]
            )
            narration = response.text.strip()
            scene["text"] = narration
            print(f"Narração gerada para {scene['image']}")
        except Exception as e:
            print(f"Erro ao gerar narração para {scene['image']}: {e}")
            
        new_scenes.append(scene)

    # Salvar o novo scenes.json
    with open(scenes_path, "w", encoding="utf-8") as f:
        json.dump({"scenes": new_scenes}, f, ensure_ascii=False, indent=4)
        
    print("Roteiro atualizado com sucesso!")

if __name__ == "__main__":
    generate_script()
