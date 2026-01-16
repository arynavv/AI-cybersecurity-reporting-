import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# --- PASTE YOUR API KEY HERE FOR THIS TEST ---
# It's okay to do this here since this is a temporary file.
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

print("Finding available models...")

# List all models and check which ones support the 'generateContent' method
for model in genai.list_models():
  if 'generateContent' in model.supported_generation_methods:
    print(f"- {model.name}")

print("\nFinished. Please use one of the model names listed above in your views.py file.")