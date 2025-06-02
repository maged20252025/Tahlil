
import streamlit as st
import os
import docx2txt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# إعداد الصفحة
st.set_page_config(page_title="البحث في أحكام المحكمة العليا", layout="wide")

# عنوان التطبيق
st.title("📚 البحث في أحكام المحكمة العليا")

# أزرار التنقل
st.markdown("""
    <style>
    .fixed-buttons {
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 9999;
    }
    .fixed-buttons button {
        margin: 5px 0;
    }
    </style>
    <div class="fixed-buttons">
        <a href="#top"><button>🔼 إلى الأعلى</button></a>
        <a href="#bottom"><button>🔽 إلى الأسفل</button></a>
    </div>
    <div id="top"></div>
""", unsafe_allow_html=True)

# حقل إدخال النص
query = st.text_area("🔍 اكتب وصف القضية أو الكلمات المفتاحية")

# تحميل الملفات من مجلد ثابت مسبقًا
BASE_DIR = "data"
documents = []
file_names = []

# قراءة الملفات من المجلد الثابت
for root, dirs, files in os.walk(BASE_DIR):
    for file in files:
        if file.endswith(".docx"):
            file_path = os.path.join(root, file)
            text = docx2txt.process(file_path)
            documents.append(text)
            file_names.append(file)

# تابع البحث
def search_documents(query, documents, file_names):
    vectorizer = TfidfVectorizer().fit_transform([query] + documents)
    cosine_similarities = cosine_similarity(vectorizer[0:1], vectorizer[1:]).flatten()
    results = sorted(zip(file_names, documents, cosine_similarities), key=lambda x: x[2], reverse=True)
    return results

# تنفيذ البحث عند الإدخال
if query:
    results = search_documents(query, documents, file_names)
    found = False
    for i, (name, content, score) in enumerate(results):
        if score > 0:
            found = True
            st.markdown(f"### 🔹 نتيجة رقم {i+1} - الملف: `{name}`")
            paragraphs = content.split("\n")
            for para in paragraphs:
                if re.search(query, para, re.IGNORECASE):
                    highlighted = re.sub(f"({query})", r"<mark>\1</mark>", para, flags=re.IGNORECASE)
                    st.markdown(f"<p style='background-color:#f9f9f9;padding:10px;border-radius:5px'>{highlighted}</p>", unsafe_allow_html=True)
    if not found:
        st.warning("لم يتم العثور على أي نتيجة مطابقة.")
    st.markdown("<div id='bottom'></div>", unsafe_allow_html=True)
else:
    st.info("يرجى إدخال وصف القضية أو كلمات مفتاحية للبحث.")
