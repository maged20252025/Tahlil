
import streamlit as st
from docx import Document
import fitz  # PyMuPDF
import io
import zipfile
import re

st.set_page_config(page_title="البحث في أحكام المحكمة العليا", layout="wide")
st.title("📚 أداة البحث في أحكام المحكمة العليا (Word + PDF)")

# تنظيف النص العربي لتوحيد المقارنة
def normalize_text(text):
    text = re.sub(r"[ًٌٍَُِّْ]", "", text)
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ة", "ه")
    text = text.replace("ـ", "")
    return text.strip()

# تظليل تكرار واحد فقط من الكلمة داخل النص
def highlight_one_hit(text, keyword, hit_index):
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    matches = list(pattern.finditer(text))
    if 0 <= hit_index < len(matches):
        match = matches[hit_index]
        start, end = match.start(), match.end()
        return (
            text[:start]
            + f"<mark style='background-color: #fff176'>{text[start:end]}</mark>"
            + text[end:]
        )
    return text

# رفع الملفات
if 'hide_files' not in st.session_state:
    st.session_state.hide_files = False

uploaded_files = None if st.session_state.hide_files else st.file_uploader(
    "📤 ارفع ملفات Word أو PDF", type=["docx", "pdf"], accept_multiple_files=True
)

if uploaded_files:
    if st.button("🗑️ حذف جميع الملفات"):
        st.session_state.hide_files = True

keywords = st.text_area("✍️ الكلمات المفتاحية (افصل كل كلمة بفاصلة)", "")
selected_file_name = None

if uploaded_files:
    filenames = [f.name for f in uploaded_files]
    selected_file_name = st.selectbox("📂 اختر ملفًا للبحث داخله أو اختر 'الكل'", ["الكل"] + filenames)

search_button = st.button("🔍 بدء البحث")

if uploaded_files and search_button:
    raw_keywords = [k.strip() for k in keywords.split(",") if k.strip()]
    keyword_list = [normalize_text(k) for k in raw_keywords]
    results = []
    matched_files = {}

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

        for paragraph_text in text_blocks:
            norm_paragraph = normalize_text(paragraph_text)
            for raw_kw, norm_kw in zip(raw_keywords, keyword_list):
                pattern = re.compile(rf"\b{re.escape(norm_kw)}\b", re.IGNORECASE)
                hits = list(pattern.finditer(norm_paragraph))
                for idx in range(len(hits)):
                    highlighted = highlight_one_hit(paragraph_text, raw_kw, idx)
                    results.append({
                        "الملف": file_name,
                        "نص": highlighted
                    })
                    matched_files[file_name] = file_bytes

    if results:
        st.success(f"✅ تم العثور على {len(results)} نتيجة في {len(matched_files)} ملف")

        for res in results:
            st.write(f"📘 **الملف:** {res['الملف']}")
            st.markdown(res["نص"], unsafe_allow_html=True)

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
