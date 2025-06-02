import streamlit as st
import os
import io
import zipfile
import docx2txt
import fitz  # PyMuPDF

# إعداد الصفحة
st.set_page_config(page_title="أداة البحث في أحكام المحكمة العليا", layout="centered", page_icon="📚")

st.markdown("<h1 style='text-align: center;'>📚 أداة البحث في أحكام المحكمة العليا (Word + PDF)</h1>", unsafe_allow_html=True)

# رفع الملفات
uploaded_files = st.file_uploader("📂 ارفع ملفات Word أو PDF", type=["pdf", "docx"], accept_multiple_files=True)

# الكلمات المفتاحية
keywords_input = st.text_area("✍️ الكلمات المفتاحية (افصل كل كلمة بفاصلة)", height=100)

# اختيار البحث في ملف معين أو الكل
target_file = st.selectbox("📁 اختر ملفًا للبحث داخله أو اختر 'الكل'", options=["الكل"] + [f.name for f in uploaded_files])

# ✅ زر تحميل كل الملفات دفعة واحدة (أعلى الصفحة)
if uploaded_files:
    zip_buffer_top = io.BytesIO()
    with zipfile.ZipFile(zip_buffer_top, "w") as zipf:
        for f in uploaded_files:
            zipf.writestr(f.name, f.read())
    zip_buffer_top.seek(0)
    st.download_button("📦 تحميل جميع الملفات دفعة واحدة", data=zip_buffer_top, file_name="all_uploaded_files.zip", mime="application/zip")

# زر تنفيذ البحث
if st.button("🔍 بدء البحث"):
    if not keywords_input.strip():
        st.warning("يرجى إدخال وصف القضية أو كلمات مفتاحية للبحث.")
        st.stop()

    keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
    results = []

    def extract_text(file):
        if file.name.endswith(".docx"):
            return docx2txt.process(file)
        elif file.name.endswith(".pdf"):
            text = ""
            pdf = fitz.open(stream=file.read(), filetype="pdf")
            for page in pdf:
                text += page.get_text()
            return text
        return ""

    for uploaded_file in uploaded_files:
        if target_file != "الكل" and uploaded_file.name != target_file:
            continue
        file_content = extract_text(uploaded_file)
        match_count = sum(file_content.count(k) for k in keywords)
        if match_count > 0:
            snippet = ""
            for keyword in keywords:
                if keyword in file_content:
                    idx = file_content.find(keyword)
                    snippet = file_content[max(0, idx - 50):idx + 200]
                    break
            results.append({
                "file_name": uploaded_file.name,
                "matches": match_count,
                "snippet": snippet.strip()
            })

    if results:
        st.success(f"✅ تم العثور على {sum(r['matches'] for r in results)} نتيجة في {len(results)} ملف")
        for res in results:
            st.write(f"📄 **الملف:** {res['file_name']}")
            st.markdown(f"🧠 **مقتطف:**\n\n{res['snippet']}")
            st.markdown("---")

        # 📦 تحميل النتائج في ملف مضغوط
        matched_files = {}
        for file in uploaded_files:
            if any(res["file_name"] == file.name for res in results):
                matched_files[file.name] = file.getvalue()

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for name, content in matched_files.items():
                zipf.writestr(name, content)
        zip_buffer.seek(0)
        st.download_button("📦 تحميل جميع الملفات التي ظهرت فيها نتائج", data=zip_buffer, file_name="matched_files.zip", mime="application/zip")
    else:
        st.warning("لم يتم العثور على أي نتائج.")

# ✅ إضافة زر تحميل كل الملفات بجوار زر حذف الملفات (أسفل الصفحة)
if uploaded_files:
    col1, col2 = st.columns(2)
    with col1:
        st.button("🗑️ حذف جميع الملفات", on_click=lambda: st.experimental_rerun())
    with col2:
        zip_buffer_bottom = io.BytesIO()
        with zipfile.ZipFile(zip_buffer_bottom, "w") as zipf:
            for f in uploaded_files:
                zipf.writestr(f.name, f.read())
        zip_buffer_bottom.seek(0)
        st.download_button("📦 تحميل جميع الملفات دفعة واحدة", data=zip_buffer_bottom, file_name="all_uploaded_files.zip", mime="application/zip")
