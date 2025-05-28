
import streamlit as st
from docx import Document

st.set_page_config(page_title="البحث في أحكام المحكمة العليا", layout="wide")

st.title("أداة البحث في أحكام المحكمة العليا")

uploaded_file = st.file_uploader("ارفع ملف Word (docx) يحتوي على قوانين", type="docx")

keywords = st.text_area("الكلمات المفتاحية (افصل كل كلمة بفاصلة)", "")

search_button = st.button("🔍 بدء البحث")

if uploaded_file and search_button:
    doc = Document(uploaded_file)
    results = []
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
    current_law = "غير معروف"

    for para in doc.paragraphs:
        paragraph_text = para.text.strip()

        # محاولة اكتشاف اسم القانون
        if "قانون" in paragraph_text and len(paragraph_text) < 100:
            current_law = paragraph_text

        for keyword in keyword_list:
            if keyword in paragraph_text:
                results.append({
                    "القانون": current_law,
                    "نص المادة": paragraph_text
                })
                break

    if results:
        st.success(f"تم العثور على {len(results)} نتيجة")

        for i, res in enumerate(results):
            with st.container():
                st.markdown(f"""
                <div style='background-color:#e3f2fd;padding:15px;margin-bottom:15px;border-radius:10px;border:1px solid #90caf9'>
                    <h5 style='color:#1a237e;'>📘 {res["القانون"]}</h5>
                    <p style='font-size:17px;line-height:1.8;text-align:right;direction:rtl;'>{res["نص المادة"]}</p>
                </div>
                """, unsafe_allow_html=True)
                st.code(res["نص المادة"], language="text")
                st.button(f"📋 نسخ المادة رقم {i+1}", key=f"copy_{i}")
    else:
        st.warning("لم يتم العثور على أي نتائج.")
