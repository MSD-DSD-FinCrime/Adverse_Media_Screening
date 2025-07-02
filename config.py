import streamlit as st

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
SEARCH_ENGINE_ID = st.secrets["GOOGLE_CSE_ID"]

NEGATIVE_KEYWORDS = [
    "money laundering",
    "fraud",
    "corruption",
    "bribery",
    "terrorism"
]
