import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

st.set_page_config(page_title="البحث في أحكام المحكمة العليا", layout="wide")

st.title("أداة البحث في أحكام المحكمة العليا")

uploaded_file = st.file_uploader("ارفع ملف PDF المدمج هنا", type="pdf")

keywords = st.text_area("الكلمات المفتاحية (افصل كل كلمة بفاصلة)", 
"شركة ذات مسؤولية محدودة, المدير, الشركاء, الحصة العينية, السجل التجاري, مخالفة القانون, الدائنين")

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    doc = fitz.open("pdf", pdf_bytes)
    results = []

    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        for keyword in keyword_list:
            if keyword in text:
                results.append({
                    "رقم الصفحة": page_num,
                    "الكلمة المطابقة": keyword,
                    "مقتطف من النص": text[:300].replace("\n", " ")
                })

    if results:
        df = pd.DataFrame(results)
        st.success(f"تم العثور على {len(df)} نتيجة")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("تحميل النتائج بصيغة CSV", csv, file_name="نتائج_البحث.csv")
    else:
        st.warning("لم يتم العثور على أي نتائج.")
