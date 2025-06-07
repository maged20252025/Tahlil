import streamlit as st from docx import Document import fitz  # PyMuPDF import io import zipfile import re

st.set_page_config(page_title="البحث في أحكام المحكمة العليا", layout="wide") st.title("📚 أداة البحث في أحكام المحكمة العليا (Word + PDF)")

إعادة ضبط حالة رفع الملفات إذا لزم

if "upload_key" not in st.session_state: st.session_state.upload_key = "initial"

زر حذف الملفات: يقوم بتغيير المفتاح وإعادة تشغيل التطبيق

if st.button("🗑️ حذف جميع الملفات"): st.session_state.upload_key = str(io.BytesIO()) st.session_state.keywords = "" st.session_state.search_triggered = False st.rerun()

تنظيف النص العربي لتوحيد المقارنة

def normalize_text(text): text = re.sub(r"[ًٌٍَُِّْ]", "", text) text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا") text = text.replace("ة", "ه") text = text.replace("ـ", "") return text.strip()

تظليل تطابق

def highlight(text, keyword): return re.sub(f"({re.escape(keyword)})", r"<mark style='background-color: #fff176'>\1</mark>", text, flags=re.IGNORECASE)

رفع الملفات بمفتاح متغير

uploaded_files = st.file_uploader("📤 ارفع ملفات Word أو PDF", type=["docx", "pdf"], accept_multiple_files=True, key=st.session_state.upload_key)

مربع الكلمات المفتاحية

keywords = st.text_area("✍️ الكلمات المفتاحية (افصل كل كلمة بفاصلة)", key="keywords")

اختيار الملف المحدد

selected_file_name = None if uploaded_files: filenames = [f.name for f in uploaded_files] selected_file_name = st.selectbox("📂 اختر ملفًا للبحث داخله أو اختر 'الكل'", ["الكل"] + filenames)

زر البحث

if st.button("🔍 بدء البحث"): st.session_state.search_triggered = True

بدء المعالجة

if uploaded_files and st.session_state.get("search_triggered"): raw_keywords = [k.strip() for k in keywords.split(",") if k.strip()] keyword_list = [normalize_text(k) for k in raw_keywords] results = [] matched_files = {}

files_to_search = uploaded_files if selected_file_name == "الكل" else [f for f in uploaded_files if f.name == selected_file_name]

for uploaded_file in files_to_search:
    file_name = uploaded_file.name
    file_ext = file_name.lower().split(".")[-1]
    text_blocks = []

    file_bytes = uploaded_file.read()
    uploaded_file.seek(0)

    if file_ext == "docx":
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            text_blocks.append(para.text.strip())
    elif file_ext == "pdf":
        pdf = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")
        for page in pdf:
            text = page.get_text()
            paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
            text_blocks.extend(paragraphs)

    for paragraph in text_blocks:
        norm_paragraph = normalize_text(paragraph)
        for raw_kw, norm_kw in zip(raw_keywords, keyword_list):
            if re.search(rf"\\b{norm_kw}\\b", norm_paragraph, re.IGNORECASE):
                highlighted = highlight(paragraph, raw_kw)
                results.append({"الملف": file_name, "نص": highlighted})
                matched_files[file_name] = file_bytes

if results:
    filtered_file = st.selectbox("📁 عرض النتائج من ملف:", ["الكل"] + sorted(set(r["الملف"] for r in results)))
    filtered_keyword = st.selectbox("🔍

