
import streamlit as st
import os
import fitz  # PyMuPDF
import docx
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import tempfile

# إعداد الصفحة
st.set_page_config(page_title="البحث الذكي في أحكام المحكمة العليا", layout="wide")

st.title("🧠 أداة البحث الذكي في أحكام المحكمة العليا")
st.write("🔍 ابحث بناءً على وصف قانوني دقيق داخل ملفات Word أو PDF.")

uploaded_files = st.file_uploader("📂 ارفع ملفات Word أو PDF", type=["docx", "pdf"], accept_multiple_files=True)

query = st.text_area("📝 أدخل وصف القضية القانوني بدقة:", height=150)
keywords = st.text_input("🔑 كلمات مفتاحية (اختياري):")

start_search = st.button("🔎 تنفيذ البحث")

def extract_text_from_pdf(file):
    text = ""
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except:
        text = ""
    return text

def extract_text_from_docx(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name
    doc = docx.Document(tmp_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    os.unlink(tmp_path)
    return text

if start_search and query and uploaded_files:
    with st.spinner("جاري المعالجة..."):
        model = SentenceTransformer("all-MiniLM-L6-v2")
        results = []

        for file in uploaded_files:
            filename = file.name
            if filename.endswith(".pdf"):
                text = extract_text_from_pdf(file)
            else:
                text = extract_text_from_docx(file)

            paragraphs = [p.strip() for p in text.split("\n") if len(p.strip()) > 30]
            if not paragraphs:
                continue

            para_embeddings = model.encode(paragraphs)
            query_embedding = model.encode([query])

            similarities = cosine_similarity(query_embedding, para_embeddings)[0]
            top_indices = similarities.argsort()[-3:][::-1]

            for idx in top_indices:
                sim_score = similarities[idx]
                if sim_score > 0.45:
                    results.append({
                        "filename": filename,
                        "score": round(sim_score, 2),
                        "snippet": paragraphs[idx]
                    })

    if results:
        st.success(f"تم العثور على {len(results)} نتيجة مشابهة:")
        for res in sorted(results, key=lambda x: x["score"], reverse=True):
            st.markdown(f"""📄 **{res['filename']}**
            🔥 درجة التطابق: {res['score']}
            📌 المقطع:  
            > {res['snippet']}
            ---
            """)
    else:
        st.warning("لم يتم العثور على نتائج متطابقة.")
