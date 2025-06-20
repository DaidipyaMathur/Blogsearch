# Blogsearch
Searches the web for blogs and skips the SEO optimised results.

## Installation Requirements

Install Uvicorn : 
```pip install uvicorn``` 
or
```pip install fastapi "uvicorn[standard]"```

Install meilisearch : 
```curl -L https://install.meilisearch.com | sh```
Launch meilisearch :
```./meilisearch --master-key="aSampleMasterKey"```
Run the main file :
```uvicorn main:app --reload```
Run the indexer file : 
```python indexer.py ```

