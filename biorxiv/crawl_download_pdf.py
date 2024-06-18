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
# @File    : crawl_download_pdf.py
# @Software: PyCharm

import json
import requests
from bs4 import BeautifulSoup
import os
import random
import time
from urllib.parse import urljoin
import sys

USER_AGENT_FILE_PATH = "user_agents.json"
BIORXIV_URL_CATEGORY = "https://www.biorxiv.org/collection"
BIORXIV_URL = "https://www.biorxiv.org"

def get_user_agents(filepath=USER_AGENT_FILE_PATH):
    with open(filepath, "r") as f:
        try:
            data = json.load(f)
            return data["user_agents"]
        except json.JSONDecodeError as e:
            sys.stdout.write(f"Error decoding JSON: {e}")
            return None

def get_random_user_agent():
    return random.choice(get_user_agents())


def crawl_and_download_pdf(category, output_folder="downloaded_pdf_files", max_pages=5):
    """ Crawls biorxiv site based on category and downloads the articles
    :param category: category to crawl, e.g., neuroscience
    :param output_folder: output folder to save the downloaded pdf files
    :param max_pages: pagination or the number of sub-pages pages to scan for
    :return: dict
    """

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    current_page = 1
    article_count = 0

    with requests.Session() as session:
        while current_page < max_pages:
            headers = {"User-Agent": get_random_user_agent()}
            category_url = f"{BIORXIV_URL_CATEGORY}/{category}?page={current_page}"

            try:
                response = session.get(category_url, headers=headers)
                response.raise_for_status()
            except requests.RequestException as e:
                sys.stdout.write(f"Failed to retrieve page {current_page + 1} for category: {category} due to: {e}")
                break

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('a', class_='highwire-cite-linked-title')

            if not articles:
                sys.stdout.write("No more publications were found.")
                break

            sys.stdout.write(f"Page {current_page + 1}: Found {len(articles)} articles in category '{category}'")

            for article in articles:
                article_title = article.text.strip()
                article_link = urljoin("https://www.biorxiv.org", article['href'])

                headers["User-Agent"] = get_random_user_agent()
                try:
                    article_response = session.get(article_link, headers=headers)
                    article_response.raise_for_status()
                except requests.RequestException as e:
                    sys.stdout.write(f"Failed to retrieve article page: {article_title} due to: {e}")
                    continue

                article_soup = BeautifulSoup(article_response.content, 'html.parser')
                pdf_link = article_soup.find('a', class_='article-dl-pdf-link')
                if pdf_link is None:
                    sys.stdout.write(f"No PDF link found for article: {article_title}")
                    continue

                pdf_url = urljoin(f"{BIORXIV_URL}", pdf_link['href'])
                download_pdf(pdf_url, article_title, output_folder)
                article_count += 1

            current_page += 1
            # add random delay, to trick like human is browsing the site
            time.sleep(random.uniform(15, 120))

    return {"message": f"Downloaded {article_count} article of category '{category}'"}


def download_pdf(pdf_url, title, output_folder):
    """Download the pdf"""
    filename = f"{title[:50]}.pdf".replace('/', '_').replace('\\', '_')
    filepath = os.path.join(output_folder, filename)

    headers = {"User-Agent": get_random_user_agent()}
    try:
        response = requests.get(pdf_url, headers=headers, stream=True)
        response.raise_for_status()
        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        sys.stdout.write(f"Downloaded: {title}")
    except requests.RequestException as e:
        sys.stdout.write(f"Failed to download {title}: {e}")

if __name__ == "__main__":
    category = sys.argv[1]
    output_folder = sys.argv[2]
    number_of_pages = int(sys.argv[3])
    crawl_and_download_pdf(category, output_folder, number_of_pages)