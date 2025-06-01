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


# دالة لمعالجة النصوص العربية
def prepare_arabic_text(text):
    if not text.strip():
        return ""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


# دالة لتشغيل الصوت باستخدام HTML5
def audio_autoplay(sound_file):
    try:
        with open(sound_file, "rb") as f:
            audio_bytes = f.read()
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        audio_html = f"""
        <audio autoplay>
        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        Your browser does not support the audio element.
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"لا يمكن تشغيل الصوت: {e}")


# دالة معدلة لتنسيق النص مع padding مختلف لكل صورة
def add_text_to_image(image, name, job, image_name):
    try:
        img = image.copy()
        draw = ImageDraw.Draw(img)

        # استخدام خط مناسب للعربية
        try:
            font = ImageFont.truetype("arial.ttf", 250)
        except:
            font = ImageFont.load_default()
            font.size=250

        # تحضير النصوص
        name_text = prepare_arabic_text(name)
        job_text = prepare_arabic_text(job)

        # قياسات الصورة
        img_width, img_height = img.size

        # حساب حجم النصوص
        name_bbox = draw.textbbox((0, 0), name_text, font=font)
        job_bbox = draw.textbbox((0, 0), job_text, font=font)

        name_width = name_bbox[2] - name_bbox[0]
        name_height = name_bbox[3] - name_bbox[1]

        job_width = job_bbox[2] - job_bbox[0]
        job_height = job_bbox[3] - job_bbox[1]

        spacing = 20

        # تحديد قيمة padding بناءً على الصورة المختارة
        padding_values = {
            "M1.jpg": 1200,
            "M2.jpg": 940,
            "M5.jpg": 570,
            "M4.jpg": 700
        }

        top_padding = padding_values.get(image_name, 570)

        # حساب المواضع
        name_x = (img_width - name_width) // 2
        name_y = top_padding

        job_x = (img_width - job_width) // 2
        job_y = name_y + name_height + spacing

        # رسم النصوص
        draw.text((name_x, name_y), name_text, font=font, fill="black")
        draw.text((job_x, job_y), job_text, font=font, fill="black")

        return img

    except Exception as e:
        st.error(f"حدث خطأ أثناء إضافة النص: {str(e)}")
        return image


# قائمة بأسماء ملفات الصور المحلية
IMAGE_FILES = ["M1.jpg", "M2.jpg", "M5.jpg", "M4.jpg"]


# الصفحة الرئيسية
# الصفحة الرئيسية
def main_page():
    st.title("تهنئة الحج 🕋")
    st.markdown("""
    <div style='text-align: left; font-size: 1.2rem;'>
    تصميم وبرمجة موسي علي كالو  تلفزيون جدة <br>
    للتواصل واتساب  0503081873
    </div>
    """, unsafe_allow_html=True)


    try:
        st.image("k2.jpg", width=300)
    except:
        st.warning("الصورة غير متوفرة")

    if st.button("اضغط لإنشاء التهنئة"):
        st.session_state.show_new_page = True
        st.session_state.play_audio = True  # تشغيل الصوت عند الدخول للصفحة
        st.rerun()


# صفحة إنشاء التهنئة
def create_page():
    # تشغيل الصوت طالما play_audio True
    if st.session_state.get('play_audio', False):
        audio_autoplay("aud.mp3")

    st.title("إنشاء التهنئة")

    # حقول الإدخال
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.name = st.text_input('ادخل اسمك', value=st.session_state.name)
    with col2:
        st.session_state.job = st.text_input('ادخل وظيفتك', value=st.session_state.job)

    st.subheader("اختر تصميم التهنئة")

    # عرض الصور في أعمدة
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
            st.error(f"حدث خطأ أثناء تحميل الصورة: {str(e)}")

    if st.session_state.get('final_image'):
        st.subheader("التصميم النهائي")
        st.image(st.session_state.final_image, width=500)

        img_bytes = io.BytesIO()
        st.session_state.final_image.save(img_bytes, format='PNG')

        # زر الحفظ مع تأثير البالونات وإيقاف الصوت
        if st.download_button(
                label="حفظ التهنئة",
                data=img_bytes.getvalue(),
                file_name="تهنئة_الحج.png",
                mime="image/png"
        ):
            st.session_state.show_balloons = True
            st.session_state.play_audio = False  # إيقاف الصوت عند الحفظ

    # عرض البالونات عند الحفظ
    if st.session_state.show_balloons:
        st.balloons()
        st.session_state.show_balloons = False

    if st.button("العودة للصفحة الرئيسية"):
        st.session_state.show_new_page = False
        st.session_state.selected_image = None
        st.rerun()


# التحكم في عرض الصفحات
if st.session_state.show_new_page:
    create_page()
else:
    main_page()
