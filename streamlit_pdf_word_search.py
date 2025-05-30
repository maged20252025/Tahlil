
import streamlit as st
from docx import Document
import fitz  # PyMuPDF
import uuid

st.set_page_config(page_title="البحث في أحكام المحكمة العليا", layout="wide")
st.title("📚 أداة البحث في أحكام المحكمة العليا (Word + PDF)")

uploaded_files = st.file_uploader("📤 ارفع ملفات Word أو PDF (حتى 50 ملف)", type=["docx", "pdf"], accept_multiple_files=True)

keywords = st.text_area("✍️ الكلمات المفتاحية (افصل كل كلمة بفاصلة)", "")

selected_file_name = None
if uploaded_files:
    filenames = [f.name for f in uploaded_files]
    selected_file_name = st.selectbox("📂 اختر ملفًا للبحث داخله أو اختر 'الكل' للبحث في جميع الملفات", ["الكل"] + filenames)

search_button = st.button("🔍 بدء البحث")

if uploaded_files and search_button:
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
    results = []
    seen_paragraphs = set()
    matched_files = set()

    files_to_search = uploaded_files if selected_file_name == "الكل" else [f for f in uploaded_files if f.name == selected_file_name]

    for uploaded_file in files_to_search:
        current_law = "قانون غير معروف"
        file_ext = uploaded_file.name.lower().split(".")[-1]
        text_blocks = []

        if file_ext == "docx":
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                text = para.text.strip()
                text_blocks.append(text)
        elif file_ext == "pdf":
            pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            for page in pdf:
                text = page.get_text()
                paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
                text_blocks.extend(paragraphs)
            uploaded_file.seek(0)

        for paragraph_text in text_blocks:
            if "قانون" in paragraph_text and len(paragraph_text) < 100:
                current_law = paragraph_text

            for keyword in keyword_list:
                if keyword in paragraph_text and paragraph_text not in seen_paragraphs:
                    seen_paragraphs.add(paragraph_text)
                    results.append({
                        "القانون": current_law,
                        "نص المادة": paragraph_text,
                        "filename": uploaded_file.name,
                        "file": uploaded_file
                    })
                    matched_files.add(uploaded_file.name)
                    break

    if results:
        st.success(f"✅ تم العثور على {len(results)} نتيجة في {len(matched_files)} ملف")

        for res in results:
            st.write(f"📘 **القانون:** {res['القانون']}")
            st.write(res["نص المادة"])
            st.code(res["نص المادة"], language='text')

        st.markdown("---")
        st.header("⬇️ تحميل الملفات التي ظهرت فيها نتائج:")
        matched_file_objs = {f.name: f for f in files_to_search if f.name in matched_files}
        for name, file_obj in matched_file_objs.items():
            st.download_button(f"📄 تحميل الملف: {name}", data=file_obj, file_name=name)
    else:
        st.warning("لم يتم العثور على أي نتائج.")
