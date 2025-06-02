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

# دالة لحقن خط Cairo في واجهة Streamlit
def inject_custom_font():
    font_path = "fonts/Cairo-Bold.ttf"
    if os.path.exists(font_path):
        with open(font_path, "rb") as f:
            encoded_font = base64.b64encode(f.read()).decode()
        css = f"""
        <style>
        @font-face {{
            font-family: 'Cairo';
            src: url(data:font/ttf;base64,{encoded_font}) format('truetype');
        }}
        html, body, [class*="css"] {{
            font-family: 'Cairo', sans-serif !important;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    else:
        st.warning("\u26a0\ufe0f لم يتم العثور على ملف الخط 'Cairo-Bold.ttf'.")

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

# دالة لتحميل الخط العربي

def load_arabic_font(font_size=100):
    font_paths = [
        "fonts/Cairo-Bold.ttf",
        "Amiri-Bold.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\trado.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, font_size)
            except Exception:
                continue
    st.warning("تعذر تحميل خط عربي عريض. سيتم استخدام الخط الافتراضي.")
    return ImageFont.load_default()

# دالة لإضافة النص للصورة
def add_text_to_image(image, name, job, image_name):
    try:
        img = image.copy()
        draw = ImageDraw.Draw(img)
        font = load_arabic_font(font_size=40)

        name_text = prepare_arabic_text(name)
        job_text = prepare_arabic_text(job)

        img_width, img_height = img.size
        name_bbox = draw.textbbox((0, 0), name_text, font=font)
        job_bbox = draw.textbbox((0, 0), job_text, font=font)

        name_width = name_bbox[2] - name_bbox[0]
        name_height = name_bbox[3] - name_bbox[1]
        job_width = job_bbox[2] - job_bbox[0]
        job_height = job_bbox[3] - job_bbox[1]

        spacing = 20
        padding_values = {
            "M1.jpg": 1200,
            "M2.jpg": 940,
            "M5.jpg": 570,
            "M4.jpg": 700
        }
        top_padding = padding_values.get(image_name, 570)

        name_x = (img_width - name_width) // 2
        name_y = top_padding
        job_x = (img_width - job_width) // 2
        job_y = name_y + name_height + spacing

        draw.text((name_x, name_y), name_text, font=font, fill="black")
        draw.text((job_x, job_y), job_text, font=font, fill="black")

        return img

    except Exception as e:
        st.error(f"حدث خطأ أثناء إضافة النص: {str(e)}")
        return image

IMAGE_FILES = ["M1.jpg", "M2.jpg", "M5.jpg", "M4.jpg"]

def main_page():
    inject_custom_font()
    st.title("تهنئة الحج 🕋")
    st.markdown("""
    <div style='text-align: left; font-size: 1.2rem;'>
    تصميم وبرمجة علي ربيع     <br>  
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

def create_page():
    inject_custom_font()
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
            st.error(f"حدث خطأ أثناء تحميل الصورة: {str(e)}")

    if st.session_state.get('final_image'):
        st.subheader("التصميم النهائي")
        st.image(st.session_state.final_image, width=500)

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

if st.session_state.show_new_page:
    create_page()
else:
    main_page()
