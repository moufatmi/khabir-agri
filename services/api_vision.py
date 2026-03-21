import streamlit as st
import google.generativeai as genai
import sys
import os

from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

@st.cache_resource
def get_vision_model():
    system_instruction = """
    أنت 'المهندس الزراعي المغربي الرقمي' المتخصص في حماية النباتات (Crop Protection).
    مهمتك فحص صور أوراق المحاصيل (خاصة الزيتون، الحمضيات، اللوز، والنخيل) وتحديد الحالة الصحية بدقة.
    يجب أن يتضمن تقريرك باللغة العربية:
    1. **التشخيص الدقيق:** (الاسم العلمي والدارج للمرض أو نقص التغذية).
    2. **الخطورة:** (منخفضة/متوسطة/قصوى) مع شرح التأثير على الإنتاجية.
    3. **خطة العلاج المغربية:** (اقتراح أدوية أو مواد فعالة مرخصة في المغرب، أو طرق عضوية تقليدية فعالة).
    4. **نصيحة "الخبير":** توجيه للفلاح لتجنب العدوى مستقبلاً.

    أجب بلهجة مهنية تجمع بين الفصحى المبسطة والمصطلحات الزراعية المتداولة في المغرب (مثل 'التيرس'، 'الشرقي'، 'الرتبة').
    إذا كانت الصورة غير واضحة أو ليست لنبات، اطلب من الفلاح 'تقريب الكاميرا' وأخذ صورة واضحة في ضوء النهار.
    """
    try:
        # 2.0-flash is the latest and most powerful multimodal model
        return genai.GenerativeModel('gemini-2.0-flash', system_instruction=system_instruction)
    except:
        return genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)

vision_model = get_vision_model()

def analyze_crop_image(image_bytes: bytes, crop_name: str, context_prompt: str = "") -> str:
    """
    Sends an image to Gemini Vision to detect pests, diseases, or deficiencies.
    Includes a local fallback for quota issues (Error 429).
    """
    try:
        from io import BytesIO
        img = Image.open(BytesIO(image_bytes))
        
        prompt = f"هذه صورة تخص محصول {crop_name}. {context_prompt}\nقم بفحص الصورة وتقديم تقريرك الطبي الزراعي."
        
        response = vision_model.generate_content([prompt, img], stream=True)
        return response
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return generate_local_vision_fallback(crop_name)
        return f"Error: تعذر فحص الصورة. المشكلة: {error_msg}"

def generate_local_vision_fallback(crop_name: str) -> str:
    """
    Provides a professional local fallback response when API quota is exceeded.
    """
    fallbacks = {
        "زيتون": "بناءً على المحاصيل في جهة الشرق، قد تكون الأعراض مرتبطة بمرض 'عين الطاووس' الفطري أو نقص البورون. ننصح بفحص أسفل الأوراق ورش النحاس كإجراء وقائي حتى عودة الاتصال بخبير الذكاء الاصطناعي.",
        "ليمون": "في الحمضيات، غالباً ما تكون البقع ناتجة عن 'صانعة الأنفاق' أو نقص الحديد (اصفرار العروق). يرجى التأكد من عدم وجود حشرات صغيرة خلف الورقة.",
        "لوز": "محصول اللوز يتأثر بمرض 'التجعد' أو 'الصدأ'. ننصح بتقليل الرطوبة حول الشجرة وتجنب السقي العلوي للأوراق.",
        "نخيل": "إذا كانت هناك ثقوب أو ذبول، يجب الحذر من 'سوسة النخيل الحمراء' أو نقص البوتاسيوم. الفحص الميداني للجذع ضروري جداً."
    }
    
    advice = fallbacks.get(crop_name, "عذراً، الخبير الرقمي مشغول حالياً بسبب ضغط الطلبات (Quota Exceeded). كإجراء عام، تأكد من توازن التسميد وعدم وجود رطوبة زائدة تشجع الفطريات.")
    
    return f"LOCAL_FALLBACK: {advice}"
