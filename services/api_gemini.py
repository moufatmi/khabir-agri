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
    إعداد الكاش للسياق الثابت وتحميل الموديل.
    يتم تنفيذ هذا مرة واحدة فقط وتخزينه في ذاكرة Streamlit.
    """
    system_instruction = """
    أنت 'الخبير الزراعي' لجهة الشرق. 
    قواعدك العلمية ثابتة ومقدسة: 
    - معادلة السقي: ETc = Kc * ETo.
    - معاملات Kc: ليمون (0.85)، زيتون (0.7)، لوز (0.75)، نخيل (0.9)، عنب (0.75)، خضروات (1.05)، حبوب (1.15).
    - اللغة: اللغة العربية الفصحى فقط، بأسلوب بسيط ومباشر.
    - المرجعية: دراسات ORMVAM ومعايير WaPOR.
    - استراتيجية الري: بالنسبة للتربة الثقيلة (التيرس)، نفضل الري العميق والمتباعد لتشجيع الجذور. إذا اقترح النظام "يوم راحة" (0 ساعة)، اشرح للمزارع أن هذا أفضل لصحة النبات وقوة جذوره.
    - المهمة: تقديم نصيحة فورية بناءً على المعطيات التقنية التي ستزود بها.
    """
    
    try:
        # إنشاء الكاش (صالح لمدة ساعة)
        # ملاحظة: يتطلب حساب Pay-as-you-go في Google AI Studio
        cache = caching.CachedContent.create(
            model='models/gemini-3.1-flash-lite-preview',
            display_name='agricultural_rules_cache',
            system_instruction=system_instruction,
            contents=[],
            ttl=datetime.timedelta(minutes=60),
        )
        return genai.GenerativeModel.from_cached_content(cached_content=cache)
    except Exception as e:
        # في حالة فشل الكاش (مثلاً حساب مجاني فقط)، نرجع للموديل العادي كخيار احتياطي
        st.warning(f"ملاحظة: الكاش لم يشتغل (ربما بسبب نوع الحساب)، سنستخدم الموديل العادي. الخطأ: {e}")
        return genai.GenerativeModel('gemini-3.1-flash-lite-preview', system_instruction=system_instruction)

# الحصول على الموديل (من الكاش إذا كان متوفراً)
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
    status_msg = {"Red": "لا تسقي! المطر جاي أو الرطوبة طالعة.", 
                  "Yellow": "حضي راسك، نقص من السقي.", 
                  "Green": "سقي دابا."}[traffic_light]
                  
    # نمرر فقط المعطيات المتغيرة في كل طلب لتوفير التكلفة والوقت
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
    مثال: "بما أن مضختك تعطي {weather.get('pump_rate', 'X')} لتر في الساعة وأرضك تبلغ مساحتها {area} هكتار، فيجب تشغيلها لمدة {pumping_hours} ساعات..."
    استخدم اللغة العربية الفصحى المبسطة والمباشرة.
    """
    
    try:
        response = model.generate_content(dynamic_context, stream=stream)
        if stream:
            return response
        return response.text, None
    except Exception as e:
        if stream:
            return None
        return f"وقع خطأ مع Gemini API: {str(e)}", None

