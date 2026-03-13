import google.generativeai as genai

# حط الـ API Key ديالك هنا
genai.configure(api_key="AIzaSyAVJoT9vzcS6oeXRjh3QBovg284lWYw8TM")

try:
    print("--- قائمة الموديلات المتاحة لحسابك ---")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Name: {m.name}")
except Exception as e:
    print(f"خطأ في الاتصال: {e}")