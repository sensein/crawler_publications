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
from biorxiv.crawl_download_pdf import crawl_and_download_pdf

class TestCrawlAndDownloadPDF(unittest.TestCase):
    @patch('biorxiv.crawl_download_pdf.get_user_agents', return_value="test-agent")
    @patch('biorxiv.crawl_download_pdf.requests.Session.get')
    def test_crawl_and_download_pdf(self, mock_get, mock_get_user_agent):
        mock_category_response = MagicMock()
        mock_category_response.status_code = 200
        mock_category_response.content = '''
            <html>
            <body>
                <a class="highwire-cite-linked-title" href="https://www.biorxiv.org/content/10.1101/2024.03.04.583202v4">The structure of an Amyloid Precursor Protein_tali.</a>
            </body>
            </html>
        '''
        mock_category_response.raise_for_status = MagicMock()

        mock_article_response = MagicMock()
        mock_article_response.status_code = 200
        mock_article_response.content = '''
            <html>
            <body>
                <a class="article-dl-pdf-link" href="https://www.biorxiv.org/content/10.1101/2024.03.04.583202v4.full.pdf">Download PDF</a>
            </body>
            </html>
        '''
        mock_article_response.raise_for_status = MagicMock()


        mock_pdf_response = MagicMock()
        mock_pdf_response.status_code = 200
        mock_pdf_response.iter_content = lambda chunk_size: [b'%PDF-1.4\n1 0 obj\n<< >>\nendobj\n']  # Simulate PDF content
        mock_pdf_response.raise_for_status = MagicMock()

        mock_get.side_effect = [mock_category_response, mock_article_response, mock_pdf_response]

        category = "neuroscience"
        output_folder = "test_folder_pdf"
        max_pages = 2


        result = crawl_and_download_pdf(category, output_folder, max_pages)

        self.assertIn("Downloaded", result["message"])


        expected_filepath = os.path.join(output_folder, "The structure of an Amyloid Precursor Protein_tali.pdf")
        self.assertTrue(os.path.isfile(expected_filepath), f"{expected_filepath} does not exist")


        self.assertGreater(os.path.getsize(expected_filepath), 0, f"{expected_filepath} is empty")


        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)

    @patch('biorxiv.crawl_download_pdf.get_random_user_agent', return_value="test-agent")
    @patch('biorxiv.crawl_download_pdf.requests.Session.get')
    def test_crawl_and_download_pdf_no_pdfs(self, mock_get, mock_get_user_agent):
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
        mock_get.side_effect = [mock_category_response]


        category = "neuroscience"
        output_folder = "test_folder_empty"
        max_pages = 2

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        result = crawl_and_download_pdf(category, output_folder, max_pages)

        self.assertIn("Downloaded 0 article", result["message"])

        self.assertEqual(len(os.listdir(output_folder)), 0, "No files should have been created")


if __name__ == '__main__':
    unittest.main()
