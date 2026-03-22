import google.generativeai as genai
import sys

NEW_KEY = "AIzaSyDXlsZ3xmat11cYvzocVQR9Da42QsH57Ww"
genai.configure(api_key=NEW_KEY)

print(f"Testing New Key: {NEW_KEY[:10]}...{NEW_KEY[-5:]}")

def test_model(model_name):
    print(f"Testing {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'OK' in Arabic.")
        print(f"SUCCESS: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"FAILED: {str(e)}")
        return False

# Test the high-performance model we want to use
test_model('gemini-2.0-flash-lite')
