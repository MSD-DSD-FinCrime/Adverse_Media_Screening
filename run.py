from search_agent import read_entities, run_search

if __name__ == "__main__":
    try:
        entities = read_entities(r"input_data/input_customer_data.xlsx")
        print(f"✅ Found {len(entities)} entities: {entities}")
        
        if not entities:
            print("⚠️ No entities found. Please check 'entities.xlsx'")
        else:
            df_results = run_search(entities)
            print(f"✅ Total {len(df_results)} top results. Saving to Excel...")
            df_results.to_excel("results.xlsx", index=False)
            print("✅ Results saved to results.xlsx")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
