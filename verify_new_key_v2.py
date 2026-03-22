import google.generativeai as genai
import sys

NEW_KEY = "AIzaSyDXlsZ3xmat11cYvzocVQR9Da42QsH57Ww"
genai.configure(api_key=NEW_KEY)

def test_model(model_name):
    print(f"Testing {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'OK'.")
        print(f"SUCCESS {model_name}: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"FAILED {model_name}: {str(e)}")
        return False

test_model('gemini-1.5-flash')
test_model('gemini-1.5-pro')
test_model('gemini-1.0-pro')
