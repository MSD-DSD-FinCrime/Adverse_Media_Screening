import streamlit as st
import pandas as pd
from search_agent import run_search
import tempfile
import os
os.environ["LANGCHAIN_PROJECT"]=os.environ["LANGCHAIN_PROJECT"]
os.environ["LANGCHAIN_TRACING_V2"]="true"

st.set_page_config(
    page_title="Adverse Media Screening",
    page_icon="🕵️‍♂️",
    layout="centered"
)

# 🎨 Custom CSS for full background + light text
st.markdown("""
    <style>
    html, body, .stApp {
        height: 100%;
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #f5f5f5;
        font-family: 'Segoe UI', sans-serif;
    }
    .block-container {
        padding: 3rem 2rem;
        border-radius: 12px;
    }
    h1, h4, h5, h6 {
        color: #ffffff;
        text-align: center;
    }
    .stFileUploader > div {
        border: 2px dashed #8fd3f4;
        padding: 1.5rem;
        border-radius: 12px;
        background-color: rgba(255, 255, 255, 0.05);
        color: #ffffff;
    }
    .stDownloadButton button {
        background-color: #1f77b4;
        color: white;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
    }
    .uploaded {
        font-size: 1.1rem;
        color: #aaf0d1;
    }
    .stDataFrame {
        background-color: white;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 🧠 Title & Header
st.markdown("<h1>🕵️ Adverse Media Screening Tool</h1>", unsafe_allow_html=True)

st.markdown("---")

# 📁 Upload Section
st.markdown("### 📤 Upload Excel File")
uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    try:
        df_input = pd.read_excel(uploaded_file)
        if "EntityName" not in df_input.columns:
            st.error("❌ Column 'EntityName' not found.")
        else:
            entities = df_input["EntityName"].dropna().tolist()
            st.markdown(f"<div class='uploaded'>✅ {len(entities)} entities detected. Starting screening...</div>", unsafe_allow_html=True)

            with st.spinner("🔎 Screening media sources... please wait."):
                df_result = run_search(entities)

            if df_result.empty:
                st.warning("⚠️ No results found.")
            else:
                st.markdown("<div style='color: white; font-size: 1.1rem; padding: 10px 0;'>🎉 Screening complete! View or download the results below.</div>",unsafe_allow_html=True)


                st.dataframe(df_result, use_container_width=True)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                    df_result.to_excel(tmp.name, index=False)
                    tmp_path = tmp.name

                with open(tmp_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Results",
                        data=f,
                        file_name="adverse_media_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
    except Exception as e:
        st.markdown(f"<div style='color: white; background-color: #ff4d4f; padding: 12px; border-radius: 8px;'>❌ <b>Error:</b> {e}</div>",unsafe_allow_html=True)

else:
    st.markdown(
    "<div style='color: white; font-size: 1rem; text-align: center;'>📥 Upload an Excel file to begin.</div>",
    unsafe_allow_html=True
    )

