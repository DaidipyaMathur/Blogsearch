import meilisearch
import json

# --- Configuration ---
MEILISEARCH_URL = "http://localhost:7700"
MEILISEARCH_API_KEY = None
CLASSIFIED_FILE = "ground_truth_combined.jsonl"
INDEX_NAME = "personal_blog"

# --- Main Script ---
def main():
    print("--- Starting the Indexer Script ---")
    
    # (The client connection part is the same)
    try:
        client = meilisearch.Client(MEILISEARCH_URL, None) # Using None for the key
        print("Successfully connected to Meilisearch.")
    except Exception as e:
        print(f"Error: Could not connect to Meilisearch. Is it running?")
        print(f"Details: {e}")
        return

    # --- Changes are HERE ---
    documents_to_index = []
    doc_counter = 0  # 1. Initialize a counter
    print(f"Reading from '{CLASSIFIED_FILE}'...")
    with open(CLASSIFIED_FILE, 'r') as f:
        for line in f:
            data = json.loads(line)
            if data.get('human_label') == 'personal_blog':
                doc_counter += 1 # 2. Increment the counter for each blog post
                formatted_doc = {
                    'id': doc_counter, # 3. Use the counter as the simple, valid ID
                    'url': data['url'],
                    'title': data['title'],
                    'text': data['text']
                }
                documents_to_index.append(formatted_doc)
    
    print(f"Found {len(documents_to_index)} blog posts to index.")

    if not documents_to_index:
        print("No documents to index. Exiting.")
        return

    print(f"Sending {len(documents_to_index)} documents to the '{INDEX_NAME}' index...")
    try:
        task = client.index(INDEX_NAME).add_documents(documents_to_index, primary_key='id')
        print(f"Meilisearch task created. Task UID: {task.task_uid}")
        print("Documents are being indexed in the background.")
        
    except Exception as e:
        print(f"An error occurred while adding documents: {e}")
        return

    print("\n--- Indexing Script Finished ---")


if __name__ == "__main__":
    main()
