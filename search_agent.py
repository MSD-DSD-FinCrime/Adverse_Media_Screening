import requests
import pandas as pd
from dateutil.parser import parse as parse_date
from config import GOOGLE_API_KEY, SEARCH_ENGINE_ID, NEGATIVE_KEYWORDS

def read_entities(file_path: str) -> list:
    df = pd.read_excel(file_path)
    return df["EntityName"].dropna().tolist()

def extract_publish_date(item):
    try:
        meta_tags = item.get("pagemap", {}).get("metatags", [{}])[0]
        date_fields = ["article:published_time", "og:published_time", "pubdate", "date"]
        for field in date_fields:
            if field in meta_tags:
                return parse_date(meta_tags[field])
    except:
        pass
    try:
        snippet = item.get("snippet", "")
        return parse_date(snippet, fuzzy=True)
    except:
        return None

def search_entity(entity: str, keyword: str) -> list:
    query = f"{entity} {keyword}"
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"❌ Error {response.status_code} for query '{query}'")
        return []

    results = response.json().get("items", [])
    output = []
    for item in results:
        date = extract_publish_date(item)
        output.append({
            "Entity": entity,
            "Keyword": keyword,
            "Title": item.get("title"),
            "Snippet": item.get("snippet"),
            "Link": item.get("link"),
            "PublishDate": date
        })

    return output

def run_search(entity_list: list) -> pd.DataFrame:
    all_entity_results = []

    for entity in entity_list:
        entity_results = []

        for keyword in NEGATIVE_KEYWORDS:
            print(f"🔎 Searching: {entity} + {keyword}")
            results = search_entity(entity, keyword)
            print(f"   → Found {len(results)} results")

            # Limit to 3 results per keyword
            if results:
                entity_results.extend(results[:3])

        if not entity_results:
            continue  # Skip entity if no results at all

        df_entity = pd.DataFrame(entity_results)

        # Ensure PublishDate column exists and is datetime
        df_entity["PublishDate"] = pd.to_datetime(df_entity.get("PublishDate"), errors='coerce')

        # Separate dated and undated
        dated_articles = df_entity.dropna(subset=["PublishDate"]).copy()
        undated_articles = df_entity[df_entity["PublishDate"].isna()].copy()

        # Sort dated articles (most recent first) and make datetime timezone-unaware
        dated_articles = dated_articles.sort_values(by="PublishDate", ascending=False)
        dated_articles["PublishDate"] = dated_articles["PublishDate"].apply(lambda x: x.replace(tzinfo=None))

        # Combine: prefer dated articles, then undated to make total = 10
        combined = pd.concat([dated_articles, undated_articles], ignore_index=True).head(10)

        all_entity_results.append(combined)

    # Combine all entity results
    if all_entity_results:
        final_df = pd.concat(all_entity_results, ignore_index=True)
        return final_df
    else:
        return pd.DataFrame()
