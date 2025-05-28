
import streamlit as st
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="البحث في أحكام المحكمة العليا", layout="wide")

st.title("أداة البحث في أحكام المحكمة العليا")

uploaded_file = st.file_uploader("ارفع ملف PDF المدمج هنا", type="pdf")

keywords = st.text_area("الكلمات المفتاحية (افصل كل كلمة بفاصلة)", "شركة, الشركاء, القانون, مخالفة, دعوى")

search_button = st.button("🔍 بدء البحث")

if uploaded_file and search_button:
    pdf_bytes = uploaded_file.read()
    doc = fitz.open("pdf", pdf_bytes)
    results = []

    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        for keyword in keyword_list:
            for match in re.finditer(r"(.{0,50}\b" + re.escape(keyword) + r"\b.{0,50})", text):
                full_page_text = text.replace("\n", " ")
                results.append({
                    "رقم الصفحة": page_num,
                    "نص المادة": full_page_text
                })

    if results:
        st.success(f"تم العثور على {len(results)} نتيجة")

        for res in results:
            html_content = f"""
            <div style='background-color:#e8f0fe;padding:15px;margin-bottom:15px;border-radius:10px;border:1px solid #c3c3c3'>
                <h5 style='color:#1a237e;'>📄 صفحة رقم: {res["رقم الصفحة"]}</h5>
                <p style='font-size:17px;line-height:1.8;text-align:right;direction:rtl;'>{res["نص المادة"]}</p>
            </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)
    else:
        st.warning("لم يتم العثور على أي نتائج.")
