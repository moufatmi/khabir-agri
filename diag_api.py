import google.generativeai as genai
import sys
import os

# Add parent dir to path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from config import GEMINI_API_KEY
    print(f"Testing Key: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-5:]}")
except ImportError:
    print("Could not import config.py. Checking environment variables...")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found.")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)

def test_model(model_name):
    print(f"\n--- Testing Model: {model_name} ---")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'OK' in Arabic.")
        print(f"Success! Response: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"Failed: {str(e)}")
        return False

# List models first
print("Available Models for this Key:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")

# Test the ones we use in the app
test_model('gemini-2.0-flash-lite')
test_model('gemini-flash-latest')
test_model('gemini-3.1-flash-lite-preview')
