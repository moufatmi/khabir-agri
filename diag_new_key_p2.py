import google.generativeai as genai
import sys

NEW_KEY = "AIzaSyBYUxXCwgIxiz7gi1iioj1UurJPGISaXK4"
genai.configure(api_key=NEW_KEY)

print("Listing models for the NEW key...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"ERROR: {e}")

model = genai.GenerativeModel('gemini-1.5-flash-latest')
try:
    print("Testing gemini-1.5-flash-latest...")
    res = model.generate_content("Hi")
    print(f"SUCCESS: {res.text.strip()}")
except Exception as e:
    print(f"FAILED: {e}")
