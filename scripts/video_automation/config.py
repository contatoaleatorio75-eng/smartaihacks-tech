import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env com override para garantir que a chave nova seja usada
load_dotenv(override=True)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'), override=True)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

if ELEVENLABS_API_KEY:
    print(f"Key ElevenLabs carregada: {ELEVENLABS_API_KEY[:6]}...{ELEVENLABS_API_KEY[-4:]}")
else:
    print("AVISO: ELEVENLABS_API_KEY não encontrada no arquivo .env")
