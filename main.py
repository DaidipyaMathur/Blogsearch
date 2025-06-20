import meilisearch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Configuration ---
MEILISEARCH_URL = "http://localhost:7700"
MEILISEARCH_API_KEY = None
INDEX_NAME = "personal_blog"

# --- FastAPI App Setup ---
# Create the FastAPI app instance
app = FastAPI()

# Connect to Meilisearch
client = meilisearch.Client(MEILISEARCH_URL, MEILISEARCH_API_KEY)

# --- CORS Middleware ---
# This allows our HTML file (on a different "origin") to talk to our backend API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for local development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoint ---
# This defines our main search endpoint.
# It will be accessible at http://localhost:8000/search
@app.get("/search")
def search_blogs(q: str):
    """
    Searches the 'personal_blog' index in Meilisearch.
    'q' is the query parameter from the URL (e.g., /search?q=my-query)
    """
    try:
        search_results = client.index(INDEX_NAME).search(q)
        return search_results
    except Exception as e:
        return {"error": str(e)}

print("--- FastAPI server is ready ---")
print("Run this with: uvicorn main:app --reload")
print("Access the search UI by opening the 'index.html' file in your browser.")
