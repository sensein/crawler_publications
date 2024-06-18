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
# @File    : test_crawl_extract_metadata_csv.py
# @Software: PyCharm

import unittest
import biorxiv.crawl_extract_metadata_csv as crawl_extract_metadata_csv
from biorxiv.crawl_extract_metadata_csv import extract_article_info

class TestExtractArticleInfo(unittest.TestCase):

    def test_extract_article_info_success(self):

        url = "https://www.biorxiv.org/content/10.1101/2024.06.12.598720v3"
        result = extract_article_info(url, 'biorxiv/user_agents.json')

        expected_result = [
            'Studying time-resolved functional connectivity via communication theory: on the complementary nature of phase synchronization and sliding window Pearson correlation.',
            '10.1101/2024.06.12.598720', 'Sir-Lord   Wiafe, Nana   Asante, Vince   Calhoun, Ashkan   Faghiri',
            '2024/01/01',
            'The copyright holder for this preprint is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under a CC-BY-NC-ND 4.0 International license.']

        self.assertEqual(result, expected_result)

    def test_extract_article_info_failure(self):
        url = "https://invalid.url"
        result = extract_article_info(url, 'biorxiv/user_agents.json')
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
