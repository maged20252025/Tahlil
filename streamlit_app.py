
import streamlit as st
import docx
import re

st.set_page_config(page_title="البحث في أحكام المحكمة العليا", layout="wide")

st.title("أداة البحث في أحكام المحكمة العليا")

uploaded_file = st.file_uploader("ارفع ملف Word (docx) هنا", type="docx")

keywords = st.text_area("الكلمات المفتاحية (افصل كل كلمة بفاصلة)", "")

search_button = st.button("🔍 بدء البحث")

if uploaded_file and search_button:
    doc = docx.Document(uploaded_file)
    full_text = ""
    for para in doc.paragraphs:
        full_text += para.text + "\n"

    results = []
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]

    for keyword in keyword_list:
        for match in re.finditer(r"(.{0,50}\b" + re.escape(keyword) + r"\b.{0,50})", full_text):
            context = match.group(1).replace("\n", " ")
            results.append({
                "نص المادة": context
            })

    if results:
        st.success(f"تم العثور على {len(results)} نتيجة")

        for res in results:
            html_content = f"""
            <div style='background-color:#e8f0fe;padding:15px;margin-bottom:15px;border-radius:10px;border:1px solid #c3c3c3'>
                <p style='font-size:17px;line-height:1.8;text-align:right;direction:rtl;'>{res["نص المادة"]}</p>
            </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)
    else:
        st.warning("لم يتم العثور على أي نتائج.")
