
import streamlit as st
import os
import docx2txt
import fitz  # PyMuPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import zipfile
import io

st.set_page_config(page_title="أداة البحث في أحكام المحكمة العليا", layout="wide")

st.title("📚 أداة البحث في أحكام المحكمة العليا (Word + PDF)")

st.markdown("📤 **ارفع ملفات Word أو PDF**")
uploaded_files = st.file_uploader("Drag and drop files here", type=["pdf", "docx"], accept_multiple_files=True)

if uploaded_files:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ حذف جميع الملفات"):
            uploaded_files.clear()

    with col2:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for file in uploaded_files:
                zipf.writestr(file.name, file.getvalue())
        zip_buffer.seek(0)
        st.download_button("📦 تحميل جميع الملفات (ZIP)", data=zip_buffer, file_name="all_uploaded_files.zip", mime="application/zip")

st.markdown("✍️ **الكلمات المفتاحية (افصل كل كلمة بفاصلة)**")
keywords_input = st.text_area("الكلمات المفتاحية", height=60)

st.markdown("📂 **اختر ملفاً للبحث داخله أو اختر 'الكل'**")
selected_file = st.selectbox("اختر ملفًا للبحث داخله أو اختر 'الكل'", ["الكل"] + [file.name for file in uploaded_files])

if st.button("🔍 بدء البحث"):
    if not keywords_input.strip():
        st.warning("يرجى إدخال وصف القضية أو كلمات مفتاحية للبحث.")
    else:
        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
        if not keywords:
            st.warning("يرجى إدخال كلمات مفتاحية صحيحة.")
        else:
            def extract_text(file):
                if file.name.endswith(".docx"):
                    return docx2txt.process(file)
                elif file.name.endswith(".pdf"):
                    pdf_doc = fitz.open(stream=file.read(), filetype="pdf")
                    text = ""
                    for page in pdf_doc:
                        text += page.get_text()
                    return text
                return ""

            files_to_search = uploaded_files if selected_file == "الكل" else [file for file in uploaded_files if file.name == selected_file]
            results = []

            for file in files_to_search:
                content = extract_text(file)
                matches = [kw for kw in keywords if re.search(rf"\b{re.escape(kw)}\b", content, flags=re.IGNORECASE)]
                if matches:
                    snippet = content[:500].replace("\n", " ")
                    results.append((file.name, snippet))

            if results:
                st.success(f"✅ تم العثور على {len(results)} نتيجة في {len(results)} ملف 📂")
                for res in results:
                    st.write(f"📄 **الملف: {res[0]}**")
                    st.markdown(res[1])
                    st.markdown("---")
                st.header("⬇️ الملفات التي ظهرت فيها نتائج:")
                for name, content in results:
                    st.download_button(f"📄 تحميل الملف: {name}", data=content.encode(), file_name=name)

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zipf:
                    for name, content in results:
                        zipf.writestr(name, content)
                zip_buffer.seek(0)
                st.download_button("📦 تحميل جميع الملفات دفعة واحدة (ZIP)", data=zip_buffer, file_name="matched_files.zip", mime="application/zip")
            else:
                st.warning("🙁 لم يتم العثور على أي نتائج.")
