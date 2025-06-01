
import streamlit as st
import os
import re
import io
import base64
import docx2txt
import fitz  # PyMuPDF

# إعداد الصفحة
st.set_page_config(page_title="🔍 البحث في أحكام المحكمة العليا", layout="wide")
st.title("🔍 أداة البحث في ملفات PDF و Word")

# دالة لتوحيد النص (إزالة التشكيل والمدود)
def normalize_text(text):
    text = re.sub(r'[ًٌٍَُِّْـ]', '', text)  # Remove diacritics
    text = re.sub(r'[ـ]', '', text)  # Remove tatweel
    return text

# واجهة المستخدم
uploaded_files = st.file_uploader("📂 قم برفع الملفات (Word أو PDF)", type=["pdf", "docx"], accept_multiple_files=True)

st.markdown("### 📝 وصف البحث القانوني")
description = st.text_area("اكتب وصفًا تفصيليًا عن نوع الأحكام التي تبحث عنها", height=150)

keywords = st.text_input("🔑 الكلمات المفتاحية (افصل بينها بفاصلة)")

if st.button("ابدأ البحث"):
    if not uploaded_files:
        st.warning("يرجى رفع بعض الملفات.")
        st.stop()

    # استخراج الكلمات من مربع الوصف + مربع الكلمات المفتاحية
    description_words = [w.strip(".,،؟:؛") for w in description.split() if len(w) > 1]
    raw_keywords = [k.strip() for k in keywords.split(",") if k.strip()]
    all_keywords = list(set(raw_keywords + description_words))
    keyword_list = [normalize_text(k) for k in all_keywords]

    total_hits = 0
    matched_files = []

    for file in uploaded_files:
        file_text = ""
        if file.name.endswith(".pdf"):
            with fitz.open(stream=file.read(), filetype="pdf") as doc:
                for page in doc:
                    file_text += page.get_text()
        elif file.name.endswith(".docx"):
            file_text = docx2txt.process(file)

        normalized_text = normalize_text(file_text)
        matches = []

        for kw in keyword_list:
            spans = re.findall(rf"(.{{0,40}}{re.escape(kw)}.{{0,40}})", normalized_text)
            matches.extend(spans)

        if matches:
            matched_files.append((file.name, matches))
            total_hits += len(matches)

    # عرض النتائج
    if matched_files:
        st.success(f"تم العثور على {total_hits} نتيجة في {len(matched_files)} ملف.")
        for fname, results in matched_files:
            st.markdown(f"### 📄 {fname}")
            for res in results:
                highlighted = res
                for kw in keyword_list:
                    highlighted = re.sub(f"({re.escape(kw)})", r"**🟨\1🟨**", highlighted, flags=re.IGNORECASE)
                st.markdown(f"> {highlighted}")
            st.markdown("---")
    else:
        st.info("لم يتم العثور على نتائج مطابقة.")
