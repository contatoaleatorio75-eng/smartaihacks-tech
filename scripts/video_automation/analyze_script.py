import os
import json
from google import genai
from config import GEMINI_API_KEY

def analyze_script():
    # 1. Setup
    if not GEMINI_API_KEY:
        print("❌ Erro: API Key do Gemini não configurada.")
        return

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    input_path = os.path.join("input", "full_script.txt")
    if not os.path.exists(input_path):
        print(f"❌ Erro: {input_path} não encontrado.")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    # 2. Prompt para o Gemini
    prompt = f"""
    Você é um editor de vídeo IA. Analise o seguinte roteiro e divida-o em cenas visuais de aproximadamente 5 a 10 segundos de leitura (ou por sentenças lógicas).
    Para cada cena, forneça:
    1. O trecho de texto exato.
    2. Uma query de busca em INGLÊS otimizada para buscar vídeos de stock (Pexels/Shutterstock) que ilustrem o que está sendo dito. Seja específico visualmente.
    
    Retorne APENAS um JSON válido no seguinte formato:
    {{
        "scenes": [
            {{
                "text": "Texto da sentença...",
                "search_query": "visual description for stock footage"
            }}
        ]
    }}

    Roteiro:
    {full_text}
    """

    print("🤖 Analisando roteiro com Gemini...")
    
    import time
    
    max_retries = 3
    retry_delay = 10
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite-001", 
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )
            
            # 3. Salvar resultado
            scenes_data = response.text
            # Clean up Markdown code blocks if present
            if scenes_data.startswith("```json"):
                scenes_data = scenes_data[7:]
            if scenes_data.endswith("```"):
                scenes_data = scenes_data[:-3]
                
            parsed = json.loads(scenes_data)
            
            output_path = os.path.join("output", "scenes.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=4, ensure_ascii=False)
                
            print(f"✅ Análise concluída! {len(parsed['scenes'])} cenas geradas em: {output_path}")
            break # Success, exit loop

        except Exception as e:
            print(f"⚠️ Erro na tentativa {attempt + 1}/{max_retries}: {e}")
            if "429" in str(e) or "Resource exhausted" in str(e):
                print(f"⏳ Aguardando {retry_delay} segundos...")
                time.sleep(retry_delay)
                retry_delay *= 2 # Exponential backoff
            else:
                print("❌ Erro não recuperável.")
                break



if __name__ == "__main__":
    analyze_script()
