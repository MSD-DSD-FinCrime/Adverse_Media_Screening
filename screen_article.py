import pandas as pd
import time
import json
import re
import streamlit as st

from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

def build_prompt(entity, article_text):
    return f"""
You are a financial crime analyst. Analyze the article and:

1. Summarize it in 5-6 bullet points.
2. Classify it as "Negative" or "False Hit".
3. Explain your reasoning.

Return ONLY valid JSON in this format:
{{
  "Summary": ["...", "..."],
  "IsNegative": true or false,
  "Reason": "your reason"
}}

Entity: {entity}
Article:
{article_text}
"""

def extract_article_text(url):
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        return docs[0].page_content if docs else ""
    except Exception as e:
        st.warning(f"❌ Failed to load {url}: {e}")
        return ""

def safe_parse_json(response_content, link):
    try:
        content = response_content.strip()
        if content.startswith("{"):
            return json.loads(content)
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("No valid JSON found")
    except Exception as e:
        st.warning(f"⚠️ JSON parsing failed for {link}: {e}")
        return None

def process_articles(file_path, output_path="screened_results.xlsx"):
    df = pd.read_excel(file_path)
    output_rows = []

    for index, row in df.iterrows():
        entity, link = row.get("Entity"), row.get("Link")
        if not entity or not link:
            continue
        st.write(f"🔍 Processing: {entity} - {link}")
        text = extract_article_text(link)
        if not text.strip():
            continue
        prompt = build_prompt(entity, text[:6000])
        try:
            result = llm.invoke(prompt)
            parsed = safe_parse_json(result.content, link)
            if parsed:
                output_rows.append({
                    "Entity": entity,
                    "Link": link,
                    "Summary": "\n".join(parsed.get("Summary", [])),
                    "Classification": "Negative" if parsed.get("IsNegative") else "False Hit",
                    "Reason": parsed.get("Reason", "")
                })
        except Exception as e:
            st.error(f"LLM Error: {e}")
        time.sleep(1.5)

    if output_rows:
        final_df = pd.DataFrame(output_rows)
        final_df.to_excel(output_path, index=False)
        return final_df
    else:
        return pd.DataFrame()
