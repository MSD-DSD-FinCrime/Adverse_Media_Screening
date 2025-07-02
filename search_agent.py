import requests
import pandas as pd
from dateutil.parser import parse as parse_date
from config import GOOGLE_API_KEY, SEARCH_ENGINE_ID, NEGATIVE_KEYWORDS
import streamlit as st

def extract_publish_date(item):
    try:
        meta_tags = item.get("pagemap", {}).get("metatags", [{}])[0]
        for field in ["article:published_time", "og:published_time", "pubdate", "date"]:
            if field in meta_tags:
                return parse_date(meta_tags[field])
    except:
        pass
    try:
        return parse_date(item.get("snippet", ""), fuzzy=True)
    except:
        return None

def search_entity(entity: str, keyword: str) -> list:
    query = f"{entity} {keyword}"
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": GOOGLE_API_KEY, "cx": SEARCH_ENGINE_ID, "q": query}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        st.error(f"❌ Error {response.status_code} for query '{query}'")
        return []

    results = response.json().get("items", [])
    output = []
    for item in results:
        output.append({
            "Entity": entity,
            "Keyword": keyword,
            "Title": item.get("title"),
            "Snippet": item.get("snippet"),
            "Link": item.get("link"),
            "PublishDate": extract_publish_date(item)
        })
    return output

def run_search(entity_list: list) -> pd.DataFrame:
    all_results = []

    for entity in entity_list:
        entity_results = []
        for keyword in NEGATIVE_KEYWORDS:
            st.text(f"🔎 {entity} + {keyword}")
            results = search_entity(entity, keyword)
            if results:
                entity_results.extend(results[:3])
        if not entity_results:
            continue

        df = pd.DataFrame(entity_results)
        df["PublishDate"] = pd.to_datetime(df.get("PublishDate"), errors='coerce')
        dated = df.dropna(subset=["PublishDate"]).sort_values(by="PublishDate", ascending=False)
        undated = df[df["PublishDate"].isna()]
        final_df = pd.concat([dated, undated], ignore_index=True).head(10)
        all_results.append(final_df)

    return pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()
