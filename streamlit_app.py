
import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
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
                context = match.group(1).replace("\n", " ")
                results.append({
                    "رقم الصفحة": page_num,
                    "مقتطف من النص": context,
                })

    if results:
        df = pd.DataFrame(results)
        st.success(f"تم العثور على {len(df)} نتيجة")
        selected_index = st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("تحميل النتائج بصيغة CSV", csv, file_name="نتائج_البحث.csv")

        selected_row = st.number_input("أدخل رقم الصف لعرض النص الكامل", min_value=0, max_value=len(df)-1, step=1)
        if st.button("عرض النص الكامل"):
            full_text = doc[df.iloc[selected_row]["رقم الصفحة"] - 1].get_text()
            st.text_area("النص الكامل للصفحة:", full_text, height=400)
    else:
        st.warning("لم يتم العثور على أي نتائج.")
