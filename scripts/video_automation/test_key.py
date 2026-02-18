from elevenlabs import ElevenLabs
import os
from dotenv import load_dotenv

def test_key():
    load_dotenv(override=True)
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ Chave não encontrada no .env")
        return
    
    print(f"🔑 Testando chave: {api_key[:6]}...{api_key[-4:]}")
    
    client = ElevenLabs(api_key=api_key)
    try:
        user = client.user.get()
        print(f"✅ Conectado como: {user.subscription.tier}")
        print(f"📊 Caracteres restantes: {user.subscription.character_count} / {user.subscription.character_limit}")
    except Exception as e:
        print(f"❌ Erro ao validar chave: {e}")

if __name__ == "__main__":
    test_key()
