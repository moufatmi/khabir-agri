import sys
import os
import streamlit as st
import google.generativeai as genai
from google.generativeai import caching
import datetime

# Add parent dir to path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import GEMINI_API_KEY

# إعداد الإطار العام لـ Gemini
genai.configure(api_key=GEMINI_API_KEY)

@st.cache_resource
def get_agricultural_model():
    """
    إعداد الموديل مع التعليمات البرمجية الأساسية.
    """
    system_instruction = """
    أنت 'الخبير الزراعي' لجهة الشرق. 
    تقوم بتحليل البيانات التقنية وتقديم نصائح ري دقيقة بناءً على معايير FAO-56.
    - معاملات Kc: ليمون (0.85)، زيتون (0.7)، لوز (0.75)، نخيل (0.9)، عنب (0.75)، خضروات (1.05)، حبوب (1.15).
    - التربة الثقيلة (التيرس): تحب الري العميق والمتباعد (Allowable Depletion).
    - اللغة: العربية الفصحى المبسطة.
    """
    # We use Flash 2.0 Lite or Flash Latest for higher free-tier quotas
    try:
        return genai.GenerativeModel('gemini-2.0-flash-lite', system_instruction=system_instruction)
    except:
        return genai.GenerativeModel('gemini-flash-latest', system_instruction=system_instruction)


# الحصول على الموديل
model = get_agricultural_model()

def get_map_pro_tip(region: str, crop: str, moisture: float) -> str:
    """
    Generate a tiny, one-sentence pro-tip for the map tooltip.
    """
    prompt = f"قدم نصيحة تقنية ومختصرة جداً (جملة واحدة) باللغة العربية الفصحى لمزارع {crop} في {region} علماً أن رطوبة التربة هي {moisture}%."
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "قم بالري الآن للحفاظ على إنتاجية المحصول."

def analyze_irrigation(user_prompt: str, weather: dict, etc: float, pumping_hours: float, traffic_light: str, region: str, crop: str, soil: str, area: float, stream: bool = False):
    """
    تحليل معطيات السقي والرد باستعمال الموديل المجهز.
    """
    tl_map = {"red": "Red", "yellow": "Yellow", "green": "Green"}
    tl = tl_map.get(str(traffic_light).strip().lower(), traffic_light)
    if tl not in ("Red", "Yellow", "Green"):
        tl = "Yellow"

    status_msg = {"Red": "لا تسقي! المطر جاي أو الرطوبة طالعة.",
                  "Yellow": "حضي راسك، نقص من السقي.",
                  "Green": "سقي دابا."}[tl]
                  
    dynamic_context = f"""
    المعطيات الحالية للمزارع:
    - المنطقة: {region}
    - المحصول: {crop}
    - مرحلة النمو: {weather.get('growth_stage')}
    - نوع التربة: {soil}
    - المساحة: {area} هكتار
    - الطقس: حرارة {weather.get('temperature')}، رطوبة {weather.get('humidity')}%. ({weather.get('description')})
    - مؤشر الري: {status_msg}
    - عدد الساعات المطلوبة لتشغيل المضخة: {pumping_hours} ساعة.
    - صبيب المضخة المستخدم: {weather.get('pump_rate', 'معروف')} لتر/ساعة
    - سؤال المزارع: "{user_prompt}"
    
    أجب كخبير حقيقي باختصار (جملتين) واستخدم معطيات المزارع في جوابك ليكون مقنعاً.
    """
    
    try:
        # Note: Streaming responses cannot be easily cached by st.cache_data
        # If streaming is requested, we don't cache, but we prefer non-stream for stability here
        response = model.generate_content(dynamic_context, stream=stream)
        return response, None
    except Exception as e:
        # Check if it's a quota error or other fail
        if "429" in str(e) or "quota" in str(e).lower():
            # Smart Fallback: Generate scientific advice locally
            fallback_advice = generate_local_advice(crop, tl, pumping_hours, etc)
            return None, f"LOCAL_FALLBACK:{fallback_advice}"
            
        error_msg = f"خطأ في الاتصال بـ Gemini: {str(e)}"
        return None, error_msg

def generate_local_advice(crop, traffic, hours, etc):
    """
    محرك بديل يولد نصيحة علمية إذا توقف الذكاء الاصطناعي (لحماية العرض التقني).
    """
    if traffic == "Red":
        return f"بناءً على معايير FAO-56، لا ننصح بالري اليوم لمحصول {crop} نظراً لوجود رطوبة عالية في التربة أو توقع مطر. الري الآن قد يسبب اختناقاً للجذور."
    elif traffic == "Green" and hours > 0:
        return f"تشير الحسابات التقنية (ETc={etc} ملم) إلى حاجة محصول {crop} للماء حالياً. نوصي بتشغيل المضخة لمدة {hours} ساعة لضمان إنتاجية مثالية وتعويض تبخر اليوم."
    else: # Yellow or Skip Days
        return f"بناءً على نظام الري المتباعد (Allowable Depletion)، محصول {crop} لا يزال في وضع آمن بفضل مخزون التربة. ننصح بتأجيل الري لتشجيع الجذور على البحث عن الماء في العمق."

