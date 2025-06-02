
import streamlit as st
import os
import fitz  # PyMuPDF
import docx2txt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

st.set_page_config(page_title="البحث في أحكام المحكمة العليا", layout="wide")

st.title("🔍 البحث في أحكام المحكمة العليا اليمنية")

BASE_DIR = "احكام"

def read_docx_file(file_path):
    try:
        text = docx2txt.process(file_path)
        return text.replace('\n', ' ').strip()
    except Exception as e:
        return ""

@st.cache_resource
def load_documents():
    documents = []
    filenames = []
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".docx"):
                full_path = os.path.join(root, file)
                text = read_docx_file(full_path)
                if text.strip():
                    documents.append(text)
                    filenames.append(file)
    return documents, filenames

documents, filenames = load_documents()

user_input = st.text_area("📝 أدخل وصف القضية أو الكلمات المفتاحية", height=200)

if user_input and documents:
    vectorizer = TfidfVectorizer().fit_transform([user_input] + documents)
    similarities = cosine_similarity(vectorizer[0:1], vectorizer[1:]).flatten()
    top_indices = similarities.argsort()[::-1]
    
    top_k = st.slider("🔢 عدد النتائج المعروضة", 1, 50, 10)
    st.subheader("🔎 النتائج:")
    for idx in top_indices[:top_k]:
        st.markdown("---")
        st.markdown(f"📄 **اسم الملف:** {filenames[idx]}")
        st.markdown(f"""🧠 **مقتطف:**  
{documents[idx][:500]}...""")

    # زر تحميل جميع الملفات
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        with open("all_filenames.txt", "w", encoding="utf-8") as f:
            for name in filenames:
                f.write(name + "\n")
        with open("all_filenames.txt", "rb") as file:
            st.download_button("⬇️ تحميل جميع الملفات", file, "جميع الأحكام.txt")
    with col2:
        if st.button("🗑️ حذف جميع الملفات من القائمة"):
            st.cache_resource.clear()
            st.experimental_rerun()
