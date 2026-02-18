import os
import json
from elevenlabs import ElevenLabs
from config import ELEVENLABS_API_KEY

def generate_narration():
    # 1. Configurar cliente
    if not ELEVENLABS_API_KEY:
        print("❌ Erro: API Key não configurada.")
        return

    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    # 2. Ler scenes.json
    scenes_path = os.path.join("output", "scenes.json")
    if not os.path.exists(scenes_path):
        print(f"❌ Erro: Arquivo {scenes_path} não encontrado.")
        return

    with open(scenes_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        scenes = data.get("scenes", [])

    print(f"🎤 Encontradas {len(scenes)} cenas para narração.")
    
    output_dir = os.path.join("output", "audio")
    os.makedirs(output_dir, exist_ok=True)

    # 3. Gerar áudio por cena
    for i, scene in enumerate(scenes):
        text = scene.get("text")
        if not text:
            continue
            
        filename = f"scene_{i:03d}.mp3"
        output_path = os.path.join(output_dir, filename)
        
        if os.path.exists(output_path):
            print(f"⏩ Cena {i} já existe: {filename}")
            continue
            
        print(f"🎤 Gerando áudio para Cena {i} ({len(text)} chars)...")
    
        try:
            audio_generator = client.text_to_speech.convert(
                voice_id="pNInz6obpgDQGcFmaJgB", # Adam - Dominant, Firm
                output_format="mp3_44100_128",
                text=text,
                model_id="eleven_multilingual_v2" # Using V2 standard
            )
    
            # Salvar
            with open(output_path, "wb") as f:
                for chunk in audio_generator:
                    f.write(chunk)
                    
            print(f"✅ Salvo: {filename}")
    
        except Exception as e:
            print(f"❌ Erro na Cena {i}: {e}")

if __name__ == "__main__":
    generate_narration()
