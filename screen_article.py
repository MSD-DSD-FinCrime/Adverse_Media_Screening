def process_articles(file_path, output_path="screened_results.xlsx", progress_callback=None):
    df = pd.read_excel(file_path)
    output_rows = []
    total = len(df)

    for i, row in enumerate(df.itertuples(), start=1):
        entity, link = row.Entity, row.Link
        if not entity or not link:
            continue

        # Hide this line (used for logs only)
        # st.write(f"🔍 Processing: {entity} - {link}")

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
            pass  # Optional: log to file or suppress in UI

        if progress_callback:
            progress_callback(i, total)

        time.sleep(1.5)

    if output_rows:
        final_df = pd.DataFrame(output_rows)
        final_df.to_excel(output_path, index=False)
        return final_df
    else:
        return pd.DataFrame()
