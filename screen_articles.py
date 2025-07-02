import pandas as pd
from dotenv import load_dotenv
import os
import time
import json
import re

from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

def build_prompt(entity, article_text):
    return f"""
You are a financial crime analyst. Analyze the article and:

1. Summarize it in 5-6 bullet points.
2. Classify it as "Negative" (real crime-related info) or "False Hit" (irrelevant/misleading).
3. Explain your reasoning.

IMPORTANT: Return ONLY valid JSON with double quotes and no extra explanation.
Use this format:
{{
  "Summary": ["...", "...", "..."],
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
        print(f"❌ Failed to load {url}: {e}")
        return ""

def safe_parse_json(response_content, link):
    try:
        content = response_content.strip()

        # Try direct parse
        if content.startswith("{"):
            return json.loads(content)

        # Try to extract JSON block from mixed text
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            return json.loads(match.group())

        raise ValueError("No valid JSON found")

    except Exception as e:
        print(f"⚠️ JSON parsing failed for {link}: {e}")
        with open("llm_raw_output.txt", "a", encoding="utf-8") as f:
            f.write(f"\n\n=== {link} ===\n{response_content}\n")
        return None

def process_articles(file_path):
    df = pd.read_excel(file_path)
    output_rows = []  # Collect only valid rows

    for index, row in df.iterrows():
        entity = row.get("Entity")
        link = row.get("Link")

        if not entity or not link:
            print(f"⚠️ Skipping row {index} — missing entity or link.")
            continue

        print(f"🔍 Processing {entity} - {link}")
        text = extract_article_text(link)

        if not text.strip():
            print(f"⚠️ No content extracted from {link}")
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
            else:
                print(f"⚠️ Skipping {link} — invalid LLM response.")

        except Exception as e:
            print(f"⚠️ LLM error for {link}: {e}")

        time.sleep(1.5)

    # Save only valid results
    if output_rows:
        final_df = pd.DataFrame(output_rows)
        final_df.to_excel("screened_results.xlsx", index=False)
        print("✅ Saved screened results with valid JSON only.")
    else:
        print("⚠️ No valid results to save.")

if __name__ == "__main__":
    process_articles("results.xlsx")
