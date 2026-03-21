import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.api_vision import analyze_crop_image

def render_vision_dashboard(selected_crop: str):
    st.markdown(f"""
    <div style="background-color: #161B22; border: 1px solid #30363D; border-radius: 15px; padding: 20px; margin-bottom: 20px; border-right: 5px solid #238636;">
        <h2 style="color: #FFFFFF; margin: 0;">📸 عين الخبير (التشخيص الذكي)</h2>
        <p style="color: #8B949E; margin-top: 10px;">ارفع صورة لورقة مريضة ليقوم الخبير بتشخيصها فوراً باستخدام Gemini 2.0 Flash.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="metric-card" style="text-align: right;">
            <p style="color: #58A6FF; font-weight: bold; margin-bottom: 10px;">💡 نصائح لتصوير أفضل:</p>
            <ul style="color: #8B949E; font-size: 0.9rem; padding-right: 20px;">
                <li>اقترب جيداً من الورقة المصابة.</li>
                <li>تأكد من إضاءة الشمس (تجنب الظل).</li>
                <li>الصورة يجب أن تكون واضحة.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("اختر صورة للمحصول", type=["jpg", "jpeg", "png"])
        context_msg = st.text_input("ملاحظاتك (اختياري)", placeholder="مثال: يظهر هذا اللون منذ يومين...")

        if uploaded_file is not None:
            st.image(uploaded_file, caption=f"صورة {selected_crop} المرفوعة", use_container_width=True)
            
            if st.button("🔍 افحص الصورة الآن", type="primary", use_container_width=True):
                with st.spinner("جاري التحليل المعماري للورقة..."):
                    img_bytes = uploaded_file.getvalue()
                    
                    response_stream = analyze_crop_image(img_bytes, selected_crop, context_msg)
                    
                    st.markdown("""
                    <div style="background-color: #161B22; border: 1px solid #30363D; border-radius: 12px; padding: 20px; margin-top: 20px; border-right: 5px solid #238636;">
                        <h4 style="color: #238636; margin: 0;">📋 تقرير المختبر الرقمي:</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    placeholder = st.empty()
                    report_text = ""
                    
                    if isinstance(response_stream, str) and response_stream.startswith("Error"):
                        st.error(response_stream)
                    elif isinstance(response_stream, str) and response_stream.startswith("LOCAL_FALLBACK:"):
                        advice = response_stream.replace("LOCAL_FALLBACK:", "")
                        st.warning("⚠️ ضغط كبير على الخبير الرقمي حالياً. إليك تشخيصاً أولياً بناءً على نوع المحصول:")
                        st.markdown(f"""
                        <div style="background-color: #0D1117; border: 1px solid #30363D; border-radius: 12px; padding: 20px; color: #C9D1D9; line-height: 1.6;">
                            {advice}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        try:
                            for chunk in response_stream:
                                if chunk.text:
                                    report_text += chunk.text
                                    placeholder.markdown(f"""
                                    <div style="background-color: #0D1117; border: 1px solid #30363D; border-radius: 0 0 12px 12px; padding: 20px; color: #C9D1D9; line-height: 1.6;">
                                        {report_text} ▌
                                    </div>
                                    """, unsafe_allow_html=True)
                            placeholder.markdown(f"""
                            <div style="background-color: #0D1117; border: 1px solid #30363D; border-radius: 0 0 12px 12px; padding: 20px; color: #C9D1D9; line-height: 1.6;">
                                {report_text}
                            </div>
                            """, unsafe_allow_html=True)
                        except Exception as e:
                            st.warning(f"أكملنا التشخيص مع وجود تنبيهات: {str(e)}")
                            
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #58A6FF;">🔬 لماذا 'عين الخبير'؟</h3>
            <p style="color: #8B949E; font-size: 0.95rem; line-height: 1.6;">
                الري الذكي يمنع الأمراض، ولكن عند حدوث إصابة، التشخيص السريع يوفر 70% من المحصول.
            </p>
            <div style="text-align: right; margin-top: 15px;">
                <p style="color: #7EE787; font-size: 0.9rem;">✅ اكتشاف الأمراض الفطرية</p>
                <p style="color: #7EE787; font-size: 0.9rem;">✅ تحديد نقص المعادن</p>
                <p style="color: #7EE787; font-size: 0.9rem;">✅ تشخيص الآفات الحشرية</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.success("هذه الآلية توفر عليك أياماً من الانتظار وتضمن تدخلاً دقيقاً!")
