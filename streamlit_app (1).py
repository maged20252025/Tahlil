
import streamlit as st
import os
import re
import io
import base64
import docx2txt
import fitz  # PyMuPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="البحث في الأحكام القضائية", layout="wide")
st.title("🔍 البحث الذكي في الأحكام بناءً على الوصف")

# تحميل الملفات
uploaded_files = st.file_uploader("📤 قم برفع ملفات PDF للأحكام القضائية:", type="pdf", accept_multiple_files=True)

# إدخال الوصف القانوني
query_text = st.text_area("📝 أدخل وصف القضية القانوني بدقة:", height=150, placeholder="مثال: أحكام ترفض دعاوى فرز وتجنيب إذا ثبت وجود قسمة رضائية فعلية...")

# إدخال كلمات مفتاحية (اختياري)
keywords = st.text_input("🔑 كلمات مفتاحية (اختياري):", placeholder="فرز، تجنيب، قسمة، رضائية")

# زر تنفيذ البحث
if st.button("🔍 تنفيذ البحث") and uploaded_files and query_text:

    def extract_text_from_pdf(file):
        try:
            doc = fitz.open(stream=file.read(), filetype="pdf")
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            return full_text
        except Exception as e:
            return ""

    # جمع البيانات
    documents = []
    filenames = []
    for file in uploaded_files:
        text = extract_text_from_pdf(file)
        if text:
            paragraphs = [p.strip() for p in re.split(r'[\n\r]{2,}|\n', text) if len(p.strip()) > 30]
            for para in paragraphs:
                documents.append(para)
                filenames.append(file.name)

    # إنشاء مصفوفة TF-IDF
    vectorizer = TfidfVectorizer().fit(documents + [query_text])
    doc_vectors = vectorizer.transform(documents)
    query_vector = vectorizer.transform([query_text])

    # حساب التشابه
    similarities = cosine_similarity(query_vector, doc_vectors).flatten()
    results = list(zip(filenames, documents, similarities))
    results.sort(key=lambda x: x[2], reverse=True)

    # فلترة النتائج العالية فقط
    threshold = 0.35
    filtered_results = [r for r in results if r[2] >= threshold]

    st.subheader(f"📑 تم العثور على {len(filtered_results)} نتيجة متطابقة:")

    def highlight_keywords(text, terms):
        for word in terms:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            text = pattern.sub(f"<mark>{word}</mark>", text)
        return text

    search_terms = [w.strip() for w in keywords.split(',')] if keywords else []

    for filename, paragraph, score in filtered_results:
        st.markdown(f"""
        <div style='border:1px solid #ccc; padding:10px; margin-bottom:10px; border-radius:10px;'>
            <b>📄 الملف:</b> {filename}<br>
            <b>📈 درجة التطابق:</b> {score:.2f}<br>
            <b>📌 المقطع:</b><br>
            <div style='background-color:#f9f9f9; padding:10px; border-radius:5px;'>
            {highlight_keywords(paragraph, search_terms) if search_terms else paragraph}
            </div>
        </div>
        """, unsafe_allow_html=True)

elif not uploaded_files:
    st.warning("يرجى رفع ملفات PDF أولاً.")
elif not query_text:
    st.warning("يرجى إدخال وصف قانوني للبحث.")
