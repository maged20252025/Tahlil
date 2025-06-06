
import streamlit as st
from docx import Document
import fitz  # PyMuPDF
import io
import zipfile
import re

st.set_page_config(page_title="ط§ظ„ط¨ط­ط« ظپظٹ ط£ط­ظƒط§ظ… ط§ظ„ظ…ط­ظƒظ…ط© ط§ظ„ط¹ظ„ظٹط§", layout="wide")
st.title("ًں“ڑ ط£ط¯ط§ط© ط§ظ„ط¨ط­ط« ظپظٹ ط£ط­ظƒط§ظ… ط§ظ„ظ…ط­ظƒظ…ط© ط§ظ„ط¹ظ„ظٹط§ (Word + PDF)")

# طھظ†ط¸ظٹظپ ط§ظ„ظ†طµ ط§ظ„ط¹ط±ط¨ظٹ ظ„طھظˆط­ظٹط¯ ط§ظ„ظ…ظ‚ط§ط±ظ†ط©
def normalize_text(text):
    text = re.sub(r"[ظ‘ظژظ‹ظڈظŒظگظچظ’]", "", text)
    text = text.replace("ط£", "ط§").replace("ط¥", "ط§").replace("ط¢", "ط§")
    text = text.replace("ط©", "ظ‡")
    text = text.replace("ظ€", "")
    return text.strip()

# طھط¸ظ„ظٹظ„ طھظƒط±ط§ط± ظˆط§ط­ط¯ ظپظ‚ط· ط¨ط§ط³طھط®ط¯ط§ظ… ظ…ظˆط§ط¶ط¹ start ظˆ end
def highlight_exact_hit(text, keyword, match_index):
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    matches = list(pattern.finditer(text))
    if match_index < len(matches):
        match = matches[match_index]
        start, end = match.start(), match.end()
        return (
            text[:start]
            + f"<mark style='background-color: #fff176'>{text[start:end]}</mark>"
            + text[end:]
        )
    return text

# طھظ‡ظٹط¦ط© ط­ط§ظ„ط© ط§ظ„ظ…ظ„ظپط§طھ
if 'hide_files' not in st.session_state:
    st.session_state.hide_files = False

uploaded_files = None if st.session_state.hide_files else st.file_uploader(
    "ًں“¤ ط§ط±ظپط¹ ظ…ظ„ظپط§طھ Word ط£ظˆ PDF", type=["docx", "pdf"], accept_multiple_files=True
)

if uploaded_files:
    if st.button("ًں—‘ï¸ڈ ط­ط°ظپ ط¬ظ…ظٹط¹ ط§ظ„ظ…ظ„ظپط§طھ"):
        st.session_state.hide_files = True
        st.session_state.keywords = ""
        st.session_state.search_triggered = False
        st.experimental_rerun()

keywords = st.text_area("âœچï¸ڈ ط§ظ„ظƒظ„ظ…ط§طھ ط§ظ„ظ…ظپطھط§ط­ظٹط© (ط§ظپطµظ„ ظƒظ„ ظƒظ„ظ…ط© ط¨ظپط§طµظ„ط©)", key="keywords")
selected_file_name = None

if uploaded_files:
    filenames = [f.name for f in uploaded_files]
    selected_file_name = st.selectbox("ًں“‚ ط§ط®طھط± ظ…ظ„ظپظ‹ط§ ظ„ظ„ط¨ط­ط« ط¯ط§ط®ظ„ظ‡ ط£ظˆ ط§ط®طھط± 'ط§ظ„ظƒظ„'", ["ط§ظ„ظƒظ„"] + filenames)

if st.button("ًں”چ ط¨ط¯ط، ط§ظ„ط¨ط­ط«"):
    st.session_state.search_triggered = True

if uploaded_files and st.session_state.get("search_triggered"):
    raw_keywords = [k.strip() for k in keywords.split(",") if k.strip()]
    keyword_list = [normalize_text(k) for k in raw_keywords]
    results = []
    matched_files = {}

    files_to_search = uploaded_files if selected_file_name == "ط§ظ„ظƒظ„" else [f for f in uploaded_files if f.name == selected_file_name]

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
                match_positions = list(pattern.finditer(norm_paragraph))

                visible_pattern = re.compile(re.escape(raw_kw), re.IGNORECASE)
                visible_matches = list(visible_pattern.finditer(paragraph_text))

                for idx, match in enumerate(visible_matches):
                    highlighted = (
                        paragraph_text[:match.start()]
                        + f"<mark style='background-color: #fff176'>{paragraph_text[match.start():match.end()]}</mark>"
                        + paragraph_text[match.end():]
                    )
                    results.append({
                        "ط§ظ„ظ…ظ„ظپ": file_name,
                        "ظ†طµ": highlighted
                    })
                    matched_files[file_name] = file_bytes

    if results:
        st.success(f"âœ… طھظ… ط§ظ„ط¹ط«ظˆط± ط¹ظ„ظ‰ {len(results)} ظ†طھظٹط¬ط© ظپظٹ {len(matched_files)} ظ…ظ„ظپ")

        for i, res in enumerate(results, start=1):
            with st.container():
                st.markdown(f"""
                <div style="border:1px solid #ccc; padding:10px; border-radius:10px; margin-bottom:10px; background-color:#f9f9f9;">
                <strong>ًں“„ ط§ظ„ظ†طھظٹط¬ط© {i} â€” ط§ظ„ظ…ظ„ظپ:</strong> <code>{res['ط§ظ„ظ…ظ„ظپ']}</code><br>
                <div style="margin-top:5px; font-size:15px; line-height:1.8;">{res['ظ†طµ']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.header("â¬‡ï¸ڈ طھط­ظ…ظٹظ„ ط§ظ„ظ…ظ„ظپط§طھ ط§ظ„طھظٹ ط¸ظ‡ط±طھ ظپظٹظ‡ط§ ظ†طھط§ط¦ط¬:")

        for name, content in matched_files.items():
            st.download_button(f"ًں“„ طھط­ظ…ظٹظ„ ط§ظ„ظ…ظ„ظپ: {name}", data=content, file_name=name)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for filename, content in matched_files.items():
                zipf.writestr(filename, content)
        zip_buffer.seek(0)

        st.download_button("ًں“¦ طھط­ظ…ظٹظ„ ط¬ظ…ظٹط¹ ط§ظ„ظ…ظ„ظپط§طھ ط¯ظپط¹ط© ظˆط§ط­ط¯ط© (ZIP)", data=zip_buffer, file_name="matched_files.zip")
    else:
        st.warning("ظ„ظ… ظٹطھظ… ط§ظ„ط¹ط«ظˆط± ط¹ظ„ظ‰ ط£ظٹ ظ†طھط§ط¦ط¬.")
