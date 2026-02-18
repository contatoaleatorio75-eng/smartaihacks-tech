from google import genai
from config import GEMINI_API_KEY

def list_models():
    client = genai.Client(api_key=GEMINI_API_KEY)
    print("Listing models...")
    for model in client.models.list():
        print(f"Model: {model.name}, Actions: {model.supported_actions}")

if __name__ == "__main__":
    list_models()
