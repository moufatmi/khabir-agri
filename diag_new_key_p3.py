import google.generativeai as genai
import sys

NEW_KEY = "AIzaSyDXlsZ3xmat11cYvzocVQR9Da42QsH57Ww"
genai.configure(api_key=NEW_KEY)

def test_model(model_name):
    print(f"Testing {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'SUCCESS'")
        print(f"RESULT {model_name}: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"RESULT {model_name}: FAILED {str(e)}")
        return False

test_model('gemini-flash-latest')
test_model('gemini-2.0-flash')
test_model('gemini-3.1-flash-lite-preview')
