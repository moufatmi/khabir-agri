# 🚀 دليل دمج الواجهة الاحترافية (Lovable / Blackbox.ai)

هذا الملف يحتوي على "البرومبت" الذهبي والتعليمات لدمج مشروعك مع واجهة عصرية تليق بالمرحلة الوطنية.

## 1. أين تضع هذا البرومبت؟
لا تضعه في أي ملف بالكود. هذا البرومبت يُعطى **مباشرة** لموقع [Lovable.dev](https://lovable.dev) أو [Blackbox.ai](https://www.blackbox.ai) عند البدء بإنشاء تطبيق جديد.

## 2. البرومبت المتكامل (Comprehensive Prompt)
انسخ النص التالي وألصقه هناك:

```text
Build a premium, high-end "AgTech Dashboard" for a project named 'Al-Khabir Agri'. 

CORE REQUIREMENTS:
1. Layout: Modern, clean, and RTL (Right-to-Left) supported for Arabic/Darija.
2. Main View: A map (Leaflet/Mapbox) for the farmer to select their field coordinates.
3. Dashboard Stats:
   - "Irrigation Alert": A traffic light (Green=OK, Yellow=Check, Red=Critical).
   - "Water Saved": Progress circle showing liters saved today.
   - "Economic Impact": Card showing savings in MAD (Moroccan Dirhams).
4. AI Advisor: A chat-style interface for agricultural advice with a Moroccan "Dima Maghreb" vibe. Use streaming text if possible.
5. Vision Expert: An image uploader where farmers can take pictures of plant leaves for disease diagnosis.
6. Multi-language: Support both Modern Standard Arabic and Darija.

BACKEND INTEGRATION:
The frontend must connect to a Python FastAPI backend running locally on port 8000.
- GET 'http://localhost:8000/advisor/irrigation' with params (lat, lon, crop, stage, soil, area, pump_rate).
- POST 'http://localhost:8000/advisor/vision' with params (crop, file).

Design Style: Use a "Glassmorphism" look with deep greens, whites, and gold accents. Make it look like a world-class agricultural software. No templates, must feel custom.
```

## 3. كيف يتم الربط الفعلي؟
بعد أن يُنشئ Lovable الواجهة، اتبع الخطوات التالية:

1. **تشغيل المحرك الخلفي (Backend):** 
   افتح الـ Terminal في جهازك وشغل الملف الذي أعددته لك:
   `python api_bridge.py`
   *(سيخبرك السيرفر أنه يعمل على http://0.0.0.0:8000)*

2. **التواصل:** 
   الواجهة ستطلب البيانات من `api_bridge` الذي بدوره يتصل بـ Gemini وبالأقمار الصناعية ويرجع النتيجة للواجهة.

---
**📍 ملاحظة للمرحلة الوطنية:**
الصوت المغربي الآن مدمج تلقائياً في الردود الصوتية بفضل التعديلات التي أجريتها في `api_tts.py`.
