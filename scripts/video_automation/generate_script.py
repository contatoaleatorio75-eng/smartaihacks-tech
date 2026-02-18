import os
import json
from google import genai
from config import GEMINI_API_KEY

def generate_script():
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY não encontrada.")
        return

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = """
    Create a highly detailed scene-by-scene script for a 10-12 minute YouTube video titled "The Silent Revolution: Beyond GPT-5".
    The video is a tech documentary about architectural transformations in AI.
    
    Structure:
    1. HOOK (0-15s): Provocative opening.
    2. The Scaling Plateau: Why Transformers Aren't Enough.
    3. Beyond Attention: New Foundational Architectures (Graph neural networks, Neuromorphic).
    4. The Rise of Multimodal and Embodied AI (Robotics, Agents).
    5. Computational Leaps: Novel AI Paradigms (Quantum, Optical).
    6. Societal Impact and Ethical Imperatives.
    7. OUTRO + CTA.

    Requirements:
    - Output MUST be a JSON object with a single key "scenes" which is a list.
    - Each item in "scenes" must have:
      - "text": The narration text for that scene (around 20-40 words).
      - "search_query": A Pexels-friendly search query for a video or high-quality image.
    - Total length should be enough for 10-12 minutes (calculate around 120-150 words per minute).
    - Aim for approximately 80 to 100 scenes to maintain a dynamic pace.
    - Include 3 strategic CALL TO ACTIONS (CTAs) within the narration text (e.g., "If you're finding this insightful, subscribe to SmartAIHacks for more deeper tech dives"). One around 2 minutes, one around 7 minutes, and one at the end.
    
    Format:
    {
        "scenes": [
            {"text": "...", "search_query": "..."},
            ...
        ]
    }
    
    Return ONLY the RAW JSON code. No markdown formatting.
    """

    print("🧠 Gerando roteiro longo com Gemini (Flash Latest)...")
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt
        )
        
        # Clean response text if it contains markdown markers
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        data = json.loads(text)
        
        output_path = os.path.join("output", "scenes.json")
        os.makedirs("output", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Roteiro gerado com {len(data['scenes'])} cenas em {output_path}")

    except Exception as e:
        print(f"❌ Erro ao gerar roteiro: {e}")

if __name__ == "__main__":
    generate_script()
