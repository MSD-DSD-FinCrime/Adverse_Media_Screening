import streamlit as st
import pandas as pd
from search_agent import run_search
from screen_articles import process_articles
import tempfile
import os
import altair as alt


st.set_page_config(
    page_title="Adverse Media Screening",
    page_icon="🕵️‍♂️",
    layout="centered"
)

# 🎨 Custom CSS for styling
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
st.markdown("### 📄 Upload Excel File with Entity Names")
uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    try:
        df_input = pd.read_excel(uploaded_file)
        if "EntityName" not in df_input.columns:
            st.error("❌ Column 'EntityName' not found.")
        else:
            entities = df_input["EntityName"].dropna().tolist()
            st.markdown(f"<div class='uploaded'>✅ {len(entities)} entities detected. Starting screening...</div>", unsafe_allow_html=True)

            with st.spinner("🔎 Searching articles using Google CSE..."):
                df_search_result = run_search(entities)

            if df_search_result.empty:
                st.warning("⚠️ No articles found.")
            else:
                article_count = len(df_search_result)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_search:
                    df_search_result.to_excel(tmp_search.name, index=False)
                    search_path = tmp_search.name

                st.markdown(
                    f"""
                    <div style='color: white; font-size: 1.1rem; padding: 10px 0;'>
                        ✅ {article_count} articles found. Now screening content with LLM...
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                with st.spinner("🤖 Analyzing article content using LLM..."):
                    process_articles(search_path)

                screened_path = "screened_results.xlsx"
                df_screened = pd.read_excel(screened_path)

                st.markdown("<h4>✅ Final Screening Results:</h4>", unsafe_allow_html=True)
                st.dataframe(df_screened, use_container_width=True)

                with open(screened_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Final Screened Results",
                        data=f,
                        file_name="final_screened_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                # Summary statistics
                summary_html = "<br><h4 style='color:white;'>📊 Summary:</h4>"
                summary_html += f"<div style='color:white;'>Entities processed: <b>{len(entities)}</b><br>"
                summary_html += f"Articles retrieved: <b>{article_count}</b><br>"
                summary_html += f"Articles screened: <b>{len(df_screened)}</b><br>"
                summary_html += f"Negative articles: <b>{(df_screened['Classification'] == 'Negative').sum()}</b><br>"
                summary_html += f"False hits: <b>{(df_screened['Classification'] == 'False Hit').sum()}</b></div>"
                st.markdown(summary_html, unsafe_allow_html=True)

                # Display a chart of classifications
                chart_data = df_screened["Classification"].value_counts().reset_index()
                chart_data.columns = ["Classification", "Count"]
                chart = alt.Chart(chart_data).mark_bar().encode(
                    x=alt.X("Classification", sort="-y"),
                    y="Count",
                    color="Classification"
                ).properties(
                    width=500,
                    height=300,
                    title="Classification Breakdown"
                )
                st.altair_chart(chart, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.markdown(
        "<div style='color: white; font-size: 1rem; text-align: center;'>📥 Upload an Excel file to begin.</div>",
        unsafe_allow_html=True
    )
