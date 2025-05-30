
import streamlit as st
from docx import Document
import fitz  # PyMuPDF
import uuid
import io
import zipfile
import re

st.set_page_config(page_title="البحث في أحكام المحكمة العليا", layout="wide")
st.title("📚 أداة البحث في أحكام المحكمة العليا (Word + PDF)")

# تنظيف النص من التشكيل والهمزات والتوحيد العام
def normalize_text(text):
    text = re.sub(r"[ًٌٍَُِّْـ]", "", text)  # حذف التشكيل
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ة", "ه")
    return text.strip()

# رفع الملفات
if 'hide_files' not in st.session_state:
    st.session_state.hide_files = False

uploaded_files = None if st.session_state.hide_files else st.file_uploader(
    "📤 ارفع ملفات Word أو PDF (حتى 50 ملف)", type=["docx", "pdf"], accept_multiple_files=True
)

# زر لحذف الملفات (إخفاءها فقط)
if uploaded_files:
    if st.button("🗑️ حذف جميع الملفات"):
        st.session_state.hide_files = True

keywords = st.text_area("✍️ الكلمات المفتاحية (افصل كل كلمة بفاصلة)", "")
selected_file_name = None

if uploaded_files:
    filenames = [f.name for f in uploaded_files]
    selected_file_name = st.selectbox("📂 اختر ملفًا للبحث داخله أو اختر 'الكل' للبحث في جميع الملفات", ["الكل"] + filenames)

search_button = st.button("🔍 بدء البحث")

if uploaded_files and search_button:
    keyword_list = [normalize_text(k) for k in keywords.split(",") if k.strip()]
    results = []
    seen_paragraphs = set()
    matched_files = {}

    files_to_search = uploaded_files if selected_file_name == "الكل" else [f for f in uploaded_files if f.name == selected_file_name]

    for uploaded_file in files_to_search:
        current_law = "قانون غير معروف"
        file_ext = uploaded_file.name.lower().split(".")[-1]
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

        for paragraph_text in text_blocks:
            norm_paragraph = normalize_text(paragraph_text)
            if "قانون" in norm_paragraph and len(norm_paragraph) < 100:
                current_law = paragraph_text

            for keyword in keyword_list:
                if re.search(rf"\b{re.escape(keyword)}\b", norm_paragraph):
                    if norm_paragraph not in seen_paragraphs:
                        seen_paragraphs.add(norm_paragraph)
                        results.append({
                            "القانون": current_law,
                            "نص المادة": paragraph_text,
                            "filename": uploaded_file.name
                        })
                        matched_files[uploaded_file.name] = file_bytes
                    break

    if results:
        st.success(f"✅ تم العثور على {len(results)} نتيجة في {len(matched_files)} ملف")

        for res in results:
            st.write(f"📘 **القانون:** {res['القانون']}")
            st.write(res["نص المادة"])
            st.code(res["نص المادة"], language='text')

        st.markdown("---")
        st.header("⬇️ تحميل الملفات التي ظهرت فيها نتائج:")

        for name, content in matched_files.items():
            st.download_button(f"📄 تحميل الملف: {name}", data=content, file_name=name)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for filename, content in matched_files.items():
                zipf.writestr(filename, content)
        zip_buffer.seek(0)

        st.download_button("📦 تحميل جميع الملفات دفعة واحدة (ZIP)", data=zip_buffer, file_name="matched_files.zip")
    else:
        st.warning("لم يتم العثور على أي نتائج.")
