# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# DISCLAIMER: This software is provided "as is" without any warranty,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose, and non-infringement.
#
# In no event shall the authors or copyright holders be liable for any
# claim, damages, or other liability, whether in an action of contract,
# tort, or otherwise, arising from, out of, or in connection with the
# software or the use or other dealings in the software.
# -----------------------------------------------------------------------------

# @Author  : Tek Raj Chhetri
# @Email   : tekraj@mit.edu
# @Web     : https://tekrajchhetri.com/
# @File    : crawl_extract_metadata_csv.py
# @Software: PyCharm


import requests
from bs4 import BeautifulSoup
import csv
import random
import time
import json
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
def get_user_agents(filepath="user_agents.json"):
    with open(filepath, "r") as f:
        try:
            data = json.load(f)
            return data["user_agents"]
        except json.JSONDecodeError as e:
            sys.stdout.write(f"Error decoding JSON: {e}")
            return None


# Function to get a random User-Agent
def get_random_user_agent():
    return random.choice(get_user_agents())


# Function to extract information from an article
def extract_article_info(article_link):
    headers = {"User-Agent": get_random_user_agent()}
    try:
        article_response = requests.get(article_link, headers=headers)
        article_response.raise_for_status()
    except requests.RequestException as e:
        sys.stdout.write(f"Failed to retrieve article page: {article_link} due to: {e}")
        return None

    article_soup = BeautifulSoup(article_response.content, 'html.parser')
    paper_title = article_soup.find('meta', attrs={'name': 'citation_title'})
    paper_title = paper_title['content'] if paper_title else 'N/A'

    doi = article_soup.find('meta', attrs={'name': 'citation_doi'})
    doi = doi['content'] if doi else 'N/A'

    #Remove "View ORCID Profile" from authors name as it is getting extracted
    authors_div = article_soup.find('div', class_='highwire-cite-authors')
    if authors_div:
        authors_list = []
        for author in authors_div.find_all('span', class_='highwire-citation-author'):
            # Remove "View ORCID Profile" text
            author_text = author.get_text(separator=" ").replace("View ORCID Profile", "").strip()
            authors_list.append(author_text)
        authors = ', '.join(authors_list)
    else:
        authors = 'N/A'

    # Extract posted information, i.e., the date
    posted_meta = article_soup.find('meta', attrs={'name': 'citation_publication_date'})
    posted = posted_meta['content'] if posted_meta else 'N/A'

    # Extract copyright information, i.e., the license
    copyright_info = "N/A"
    for label_div in article_soup.find_all('div', class_='field-label'):
        if 'Copyright' in label_div.text:
            copyright_info_div = label_div.find_next_sibling('div', class_='field-items')
            if copyright_info_div:
                copyright_info = copyright_info_div.text.strip()
            break

    return [paper_title, doi, authors, posted, copyright_info]


def crawl_and_extract_metadata(category, output_file="output_metadata.csv", max_pages=5, max_workers=10):
    """ Crawls biorxiv site based on category and downloads the articles metadata in csv format
    :param category: category to crawl, e.g., neuroscience
    :param output_folder: output folder to save the downloaded pdf files
    :param max_pages: pagination or the number of sub-pages pages to scan for
    :param max_workers: Concurrency limit
    :return: dict
    """
    current_page = 1

    # Open the CSV file in append mode and write the header
    with open(output_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write the header only if the file is empty
        if file.tell() == 0:
            writer.writerow(['Paper Title', 'DOI', 'Authors', 'Posted', 'Copyright'])

        with requests.Session() as session:
            while current_page <= max_pages:
                headers = {"User-Agent": get_random_user_agent()}
                category_url = f"https://www.biorxiv.org/collection/{category}?page={current_page}"

                try:
                    response = session.get(category_url, headers=headers)
                    response.raise_for_status()
                except requests.RequestException as e:
                    sys.stdout.write(f"Failed to retrieve page {current_page} for category: {category} due to: {e}")
                    break

                soup = BeautifulSoup(response.content, 'html.parser')
                articles = soup.find_all('a', class_='highwire-cite-linked-title')

                if not articles:
                    sys.stdout.write("No more articles found.")
                    break

                sys.stdout.write(f"Page {current_page}: Found {len(articles)} articles in category '{category}'")

                # Create a ThreadPoolExecutor
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Submit all tasks and collect futures
                    futures = [
                        executor.submit(extract_article_info, urljoin("https://www.biorxiv.org", article['href'])) for
                        article in articles]

                    for future in as_completed(futures):
                        result = future.result()
                        if result:
                            writer.writerow(result)
                            sys.stdout.write(f"Extracted: {result[0]}")

                current_page += 1
                time.sleep(random.uniform(5, 10))  # Random delay between 5 and 10 seconds

    return {"message": f"Data extraction completed. Output saved to {output_file}"}


if __name__ == "__main__":
    category = sys.argv[1]
    output_folder = sys.argv[2]
    number_of_pages = int(sys.argv[3])
    workers = int(sys.argv[4])
    crawl_and_extract_metadata(category=category,
                               output_file=output_folder,
                               max_pages=number_of_pages,
                               max_workers=workers)