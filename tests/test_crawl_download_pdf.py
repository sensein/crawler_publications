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
# @File    : test_crawl_download_pdf.py
# @Software: PyCharm

import unittest
from unittest.mock import patch, MagicMock
import os
# Adding the parent directory to PYTHONPATH
import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from biorxiv.crawl_download_pdf import crawl_and_download_pdf



print(f"------{sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))}")
class TestCrawlAndDownloadPDF(unittest.TestCase):
    @patch('crawl_download_pdf.get_user_agents', return_value="test-agent")
    @patch('crawl_download_pdf.requests.Session.get')
    def test_crawl_and_download_pdf(self, mock_get, mock_get_user_agent):
        # Create a mock response for the category page
        mock_category_response = MagicMock()
        mock_category_response.status_code = 200
        mock_category_response.content = '''
            <html>
            <body>
                <a class="highwire-cite-linked-title" href="/content/early/2023/01/01/12345">Article 1</a>
            </body>
            </html>
        '''
        mock_category_response.raise_for_status = MagicMock()

        mock_article_response = MagicMock()
        mock_article_response.status_code = 200
        mock_article_response.content = '''
            <html>
            <body>
                <a class="article-dl-pdf-link" href="/content/early/2023/01/01/12345.full.pdf">Download PDF</a>
            </body>
            </html>
        '''
        mock_article_response.raise_for_status = MagicMock()

        # Create a mock response for the PDF download
        mock_pdf_response = MagicMock()
        mock_pdf_response.status_code = 200
        mock_pdf_response.iter_content = lambda chunk_size: [
            b'%PDF-1.4\n1 0 obj\n<< >>\nendobj\n']  # Simulate PDF content
        mock_pdf_response.raise_for_status = MagicMock()

        # Setup the mock responses sequence
        mock_get.side_effect = [mock_category_response, mock_article_response, mock_pdf_response]

        # Define parameters for the test
        category = "neuroscience"
        output_folder = "test_folder"
        max_pages = 1

        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Run the crawl_and_download_pdf function
        result = crawl_and_download_pdf(category, output_folder, max_pages)

        # Check if the function returned the correct message
        self.assertIn("Downloaded", result["message"])

        # Check if the PDF file was created
        expected_filepath = os.path.join(output_folder, "Article 1.pdf")
        self.assertTrue(os.path.isfile(expected_filepath), f"{expected_filepath} does not exist")

        # Check if the file is non-empty
        self.assertGreater(os.path.getsize(expected_filepath), 0, f"{expected_filepath} is empty")

        # Clean up the file after the test
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)

    @patch('crawl_download_pdf.get_random_user_agent', return_value="test-agent")
    @patch('crawl_download_pdf.requests.Session.get')
    def test_crawl_and_download_pdf_no_pdfs(self, mock_get, mock_get_user_agent):
        # Create a mock response for the category page with no articles
        mock_category_response = MagicMock()
        mock_category_response.status_code = 200
        mock_category_response.content = '''
            <html>
            <body>
                <p>No articles found</p>
            </body>
            </html>
        '''
        mock_category_response.raise_for_status = MagicMock()

        # Setup the mock responses sequence
        mock_get.side_effect = [mock_category_response]

        # Define parameters for the test
        category = "neuroscience"
        output_folder = "test_folder"
        max_pages = 1

        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Run the crawl_and_download_pdf function
        result = crawl_and_download_pdf(category, output_folder, max_pages)

        # Check if the function returned the correct message for no downloads
        self.assertIn("Downloaded 0 article", result["message"])

        # Check that no PDF files were created
        self.assertEqual(len(os.listdir(output_folder)), 0, "No files should have been created")


if __name__ == '__main__':
    unittest.main()
