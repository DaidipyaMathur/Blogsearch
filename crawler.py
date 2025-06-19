#!/usr/bin/env python
# coding: utf-8





import requests
from bs4 import BeautifulSoup




# The URL of the blog post we want to crawl
start_url = "https://waitbutwhy.com/2013/10/why-procrastinators-procrastinate.html"

headers = {
    'User-Agent': 'PersonalBlogSearchCrawler/1.0'
}

html_content = ""
try:
    # A timeout is crucial to prevent our script from hanging indefinitely
    response = requests.get(start_url, headers=headers, timeout=10)

    # Raise an exception if the request was not successful (e.g., 404 Not Found, 500 Server Error)
    response.raise_for_status()

    html_content = response.text
    print("Successfully fetched the webpage!")
    print(f"Content length: {len(html_content)} characters")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")




from urllib.parse import urljoin

base_url = "https://waitbutwhy.com/2013/10/why-procrastinators-procrastinate.html"

# Use a set to store the cleaned links to automatically handle duplicates
cleaned_links = set()

if 'all_links' in locals():  # Check if all_links exists
    for link in all_links:
        href = link.get('href')

        # --- Filtering ---
        # 1. Check if the href exists and is not empty
        if not href:
            continue
        # 2. Ignore "mailto" links and javascript calls
        if href.startswith('mailto:') or href.startswith('javascript:'):
            continue
        # 3. Ignore anchor links that just point to a part of the current page
        if href.startswith('#'):
            continue

        # --- Normalizing ---
        # Use urljoin to combine the base_url with the found href.
        # urljoin is smart:
        # - If href is already absolute, it returns it unchanged.
        # - If href is relative, it joins it with the base URL correctly.
        absolute_link = urljoin(base_url, href)
        cleaned_links.add(absolute_link)

    print(f"Found {len(cleaned_links)} unique, cleaned links.")

    # Let's print the first 10 to see the result
    for link in list(cleaned_links)[:10]:
        print(link)



import time
import json
from collections import deque
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# We've wrapped all our logic into a single, reusable function

def run_targeted_crawl(seed_file, output_file, max_pages=200):
    """
    Crawls websites starting from a list of seed URLs in a file.

    Args:
        seed_file (str): The path to the file containing seed URLs (one per line).
        output_file (str): The path to the .jsonl file where results will be saved.
        max_pages (int): The maximum number of pages to crawl in this session.
    """
    print(f"--- Starting new crawl session ---")
    print(f"Seed file: {seed_file}")
    print(f"Output file: {output_file}")

    # --- Initial Setup ---
    try:
        with open(seed_file, 'r') as f:
            # Read all URLs from the seed file, stripping whitespace/newlines
            start_urls = [line.strip() for line in f if line.strip()]
        if not start_urls:
            print("Error: Seed file is empty.")
            return
    except FileNotFoundError:
        print(f"Error: Seed file not found at '{seed_file}'")
        return

    # Initialize the queue and visited set with all the seeds
    queue = deque(start_urls)
    visited_urls = set(start_urls)
    crawled_count = 0

    # Open the output file to append to
    with open(output_file, 'w') as f:
        while queue and crawled_count < max_pages:
            current_url = queue.popleft()
            crawled_count += 1

            print(f"[{crawled_count}/{max_pages}] Crawling: {current_url}")

            try:
                headers = {'User-Agent': 'PersonalBlogSearchCrawler/1.0'}
                response = requests.get(current_url, headers=headers, timeout=10)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"   -> Failed to fetch {current_url}: {e}")
                continue

            # --- Save Content ---
            soup = BeautifulSoup(response.text, 'html.parser')
            page_title = soup.find('title').get_text(strip=True) if soup.find('title') else 'No Title'
            page_text = soup.get_text(separator=' ', strip=True)

            data = {'url': current_url, 'title': page_title, 'text': page_text}
            f.write(json.dumps(data) + '\n')

            # --- Find and Add New Links ---
            for link in soup.find_all('a'):
                href = link.get('href')
                if not href: continue

                absolute_link = urljoin(current_url, href)

                # We can add more filtering logic here if needed
                if absolute_link not in visited_urls:
                    visited_urls.add(absolute_link)
                    queue.append(absolute_link)

            time.sleep(1)

    print(f"\n--- Crawl session finished. ---")
    print(f"Data for {crawled_count} pages saved to {output_file}")




# --- CRAWL 1: GATHER PERSONAL BLOGS ---
run_targeted_crawl(
    seed_file='personal_blog.txt', 
    output_file='crawled_personal.jsonl',
    max_pages=500  # Crawl up to 500 pages
)

# --- CRAWL 2: GATHER CORPORATE BLOGS ---
run_targeted_crawl(
    seed_file='personal_blog.txt', 
    output_file='crawled_personal.jsonl',
    max_pages=500  # Crawl up to 500 pages
)



import json

input_filename = "crawled_content.jsonl"
output_filename = "classified_v1_content.jsonl"

# --- Heuristic Rules ---
UTILITY_KEYWORDS = ['about', 'contact', 'store', 'shop', 'privacy', 'terms', 'support', 'faq', 'archive', 'categories', 'tags']
ARTICLE_KEYWORDS = ['leave a reply', 'post a comment', 'comments are closed', 'written by']
MIN_WORDS_THRESHOLD = 250

# --- Counters for feedback ---
class_counts = {'personal_blog': 0, 'other': 0}
processed_count = 0

print("--- Starting Heuristic Classification ---")

with open(input_filename, 'r') as infile, open(output_filename, 'w') as outfile:
    for line in infile:
        try:
            data = json.loads(line)
            processed_count += 1

            classification = 'personal_blog' # Assume it's a blog post by default

            # Rule 1: Check for utility keywords in URL and title
            url_and_title = (data.get('url', '') + ' ' + data.get('title', '')).lower()
            if any(keyword in url_and_title for keyword in UTILITY_KEYWORDS):
                classification = 'other'

            # Rule 2: Check for minimum word count (only if not already classified as 'other')
            if classification == 'personal_blog':
                word_count = len(data.get('text', '').split())
                if word_count < MIN_WORDS_THRESHOLD:
                    classification = 'other'

            # Rule 3: Check for positive article keywords (this can override an 'other' classification if signal is strong)
            if any(keyword in data.get('text', '').lower() for keyword in ARTICLE_KEYWORDS):
                classification = 'personal_blog'

            # Add the new classification to our data and write it to the new file
            data['classification_v1'] = classification
            outfile.write(json.dumps(data) + '\n')

            # Update our counters
            class_counts[classification] += 1

        except json.JSONDecodeError:
            print(f"Skipping malformed line: {line.strip()}")

print("\n--- Classification Finished ---")
print(f"Processed {processed_count} pages.")
print(f"Results saved to {output_filename}")
print("\nClassification breakdown:")
for category, count in class_counts.items():
    print(f"- {category}: {count} pages")

