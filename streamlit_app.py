
import streamlit as st
from docx import Document

st.set_page_config(page_title="البحث في أحكام المحكمة العليا", layout="wide")

st.title("أداة البحث في أحكام المحكمة العليا")

uploaded_file = st.file_uploader("ارفع ملف Word (docx) هنا", type="docx")

keywords = st.text_area("الكلمات المفتاحية (افصل كل كلمة بفاصلة)", "")

search_button = st.button("🔍 بدء البحث")

if uploaded_file and search_button:
    doc = Document(uploaded_file)
    results = []
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]

    for para in doc.paragraphs:
        paragraph_text = para.text.strip()
        for keyword in keyword_list:
            if keyword in paragraph_text:
                results.append({
                    "نص المادة": paragraph_text
                })
                break  # لا داعي لتكرار نفس الفقرة إذا وُجد فيها أكثر من كلمة

    if results:
        st.success(f"تم العثور على {len(results)} نتيجة")

        for res in results:
            html_content = f"""
            <div style='background-color:#e3f2fd;padding:15px;margin-bottom:15px;border-radius:10px;border:1px solid #90caf9'>
                <p style='font-size:17px;line-height:1.8;text-align:right;direction:rtl;'>{res["نص المادة"]}</p>
            </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)
    else:
        st.warning("لم يتم العثور على أي نتائج.")
