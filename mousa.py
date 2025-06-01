import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import io
import base64
import os

# تهيئة حالة الجلسة
if 'show_new_page' not in st.session_state:
    st.session_state.show_new_page = False
if 'name' not in st.session_state:
    st.session_state.name = ""
if 'job' not in st.session_state:
    st.session_state.job = ""
if 'selected_image' not in st.session_state:
    st.session_state.selected_image = None
if 'final_image' not in st.session_state:
    st.session_state.final_image = None
if 'show_balloons' not in st.session_state:
    st.session_state.show_balloons = False
if 'play_audio' not in st.session_state:
    st.session_state.play_audio = False

# دالة معالجة النصوص العربية المعدلة
def prepare_arabic_text(text):
    if not text.strip():
        return ""
    
    # إعدادات معالجة النص العربي
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

# دالة إضافة النص إلى الصورة (مطورة)
def add_text_to_image(image, name, job, image_name):
    try:
        # زيادة دقة الصورة إذا كانت صغيرة
        if image.width < 1500:
            img = image.resize((1500, int(1500 * (image.height/image.width))), Image.Resampling.LANCZOS)
        else:
            img = image.copy()
            
        draw = ImageDraw.Draw(img)
        
        # حساب حجم الخط ديناميكياً
        font_size = max(60, int(img.height / 10))  # حد أدنى 60
        
        # قائمة بالخطوط المحتملة (بدون استخدام ملفات خارجية)
        arabic_fonts = [
            "Arial",
            "Times New Roman",
            "Traditional Arabic",
            "Microsoft Sans Serif",
            "Segoe UI"
        ]
        
        font = None
        for font_name in arabic_fonts:
            try:
                font = ImageFont.truetype(font_name, font_size)
                break
            except:
                continue
                
        if font is None:
            font = ImageFont.load_default()
            font.size = font_size
        
        # تحضير النصوص
        name_text = prepare_arabic_text(name)
        job_text = prepare_arabic_text(job)
        
        # تحديد المواقع لكل صورة
        positions = {
            "M1.jpg": {"name_y": img.height - 400, "job_y": img.height - 250},
            "M2.jpg": {"name_y": img.height - 350, "job_y": img.height - 200},
            "M5.jpg": {"name_y": img.height - 300, "job_y": img.height - 150},
            "M4.jpg": {"name_y": img.height - 450, "job_y": img.height - 300}
        }
        
        pos = positions.get(image_name, {
            "name_y": img.height - 300,
            "job_y": img.height - 150
        })
        
        # حساب عرض النص
        name_width = draw.textlength(name_text, font=font)
        job_width = draw.textlength(job_text, font=font)
        
        # إضافة ظل للنص لتحسين الوضوح
        shadow_color = "#AAAAAA"
        draw.text(((img.width - name_width)/2 + 2, pos["name_y"] + 2), name_text, font=font, fill=shadow_color)
        draw.text(((img.width - job_width)/2 + 2, pos["job_y"] + 2), job_text, font=font, fill=shadow_color)
        
        # إضافة النص الأساسي
        text_color = "#000000"
        draw.text(((img.width - name_width)/2, pos["name_y"]), name_text, font=font, fill=text_color)
        draw.text(((img.width - job_width)/2, pos["job_y"]), job_text, font=font, fill=text_color)
        
        return img
        
    except Exception as e:
        st.error(f"حدث خطأ أثناء إضافة النص: {str(e)}")
        return image

# دالة تشغيل الصوت
def audio_autoplay(sound_file):
    try:
        with open(sound_file, "rb") as f:
            audio_bytes = f.read()
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        audio_html = f"""
        <audio autoplay>
        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"لا يمكن تشغيل الصوت: {e}")

# قائمة الصور
IMAGE_FILES = ["M1.jpg", "M2.jpg", "M5.jpg", "M4.jpg"]

# الصفحة الرئيسية
def main_page():
    st.title("تهنئة الحج 🕋")
    st.markdown("""
    <div style='text-align: left; font-size: 1.2rem;'>
    تصميم وبرمجة موسي علي كالو - تلفزيون جدة<br>
    للتواصل واتساب 0503081873
    </div>
    """, unsafe_allow_html=True)

    try:
        st.image("k2.jpg", width=300)
    except:
        st.warning("الصورة غير متوفرة")

    if st.button("اضغط لإنشاء التهنئة"):
        st.session_state.show_new_page = True
        st.session_state.play_audio = True
        st.rerun()

# صفحة الإنشاء
def create_page():
    if st.session_state.get('play_audio', False):
        audio_autoplay("aud.mp3")

    st.title("إنشاء التهنئة")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.name = st.text_input('ادخل اسمك', value=st.session_state.name)
    with col2:
        st.session_state.job = st.text_input('ادخل وظيفتك', value=st.session_state.job)

    st.subheader("اختر تصميم التهنئة")

    cols = st.columns(4)
    for i, img_file in enumerate(IMAGE_FILES):
        try:
            img = Image.open(img_file)
            with cols[i]:
                if st.session_state.name and st.session_state.job:
                    final_img = add_text_to_image(img, st.session_state.name, st.session_state.job, img_file)
                    st.image(final_img, caption=f"تصميم {i + 1}", use_container_width=True)
                else:
                    st.image(img, caption=f"تصميم {i + 1}", use_container_width=True)

                if st.button(f"اختر تصميم {i + 1}"):
                    st.session_state.selected_image = img_file
                    st.success(f"تم اختيار التصميم {i + 1}")
                    st.session_state.final_image = add_text_to_image(
                        Image.open(img_file),
                        st.session_state.name,
                        st.session_state.job,
                        img_file
                    )
        except FileNotFoundError:
            st.error(f"ملف {img_file} غير موجود")
        except Exception as e:
            st.error(f"حدث خطأ: {str(e)}")

    if st.session_state.get('final_image'):
        st.subheader("التصميم النهائي")
        st.image(st.session_state.final_image, width=800)  # عرض أكبر للصورة

        img_bytes = io.BytesIO()
        st.session_state.final_image.save(img_bytes, format='PNG')

        if st.download_button(
                label="حفظ التهنئة",
                data=img_bytes.getvalue(),
                file_name="تهنئة_الحج.png",
                mime="image/png"
        ):
            st.session_state.show_balloons = True
            st.session_state.play_audio = False

    if st.session_state.show_balloons:
        st.balloons()
        st.session_state.show_balloons = False

    if st.button("العودة للصفحة الرئيسية"):
        st.session_state.show_new_page = False
        st.session_state.selected_image = None
        st.rerun()

# التشغيل الرئيسي
if st.session_state.show_new_page:
    create_page()
else:
    main_page()
