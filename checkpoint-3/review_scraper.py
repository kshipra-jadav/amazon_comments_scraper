import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from user_agent import generate_user_agent
import pandas as pd


class AmazonScraper:
    def __init__(self):
        self.reviews_dict: dict[str, list[str, str]] = {}

    def scrape(self, amazon_url: str) -> None:
        url_dict = self.__parse_url(amazon_url)

        headers: dict[str, str] = {
            'User-Agent': generate_user_agent(),
            "accept-language": "en-GB,en;q=0.9",
        }

        content: requests.Response = requests.get(url_dict['parsed_url'], headers=headers)

        soup: BeautifulSoup = BeautifulSoup(content.text, features='html.parser')

        review_sec = soup.find(attrs={'id': 'cm-cr-dp-review-list'})

        for list_item in review_sec.find_all('li'):
            rating = list_item.find('span', class_='a-icon-alt').text
            review = list_item.find('div', class_='reviewText').span.text
            review_id = list_item.get('id')

            rating_stars = float(rating.split(' ')[0])

            self.reviews_dict[review_id] = [review, rating_stars]
        

    @staticmethod
    def __parse_url(initial_url: str) -> dict[str, str]:
        parsed = urlparse(initial_url)

        if not 'amazon' in parsed.netloc.split('.'):
            raise ValueError('Invalid URL. Please input Amazon URL')

        asin_regex = r'\b[A-Z0-9]{10}\b'
        matches = re.findall(asin_regex, parsed.path)

        if len(matches) == 0:
            raise ValueError(
                'ASIN not found in URL. Please input valid Amazon URL')

        url_dict = {
            'parsed_url': parsed.scheme + "://" + parsed.netloc + parsed.path,
            'asin': matches[0]
        }

        return url_dict

    def get_reviews_df(self) -> pd.DataFrame:
        if len(self.reviews_dict.keys()) == 0:
            raise ValueError("Pleae Scrape Reviews First")
        df = pd.DataFrame.from_dict(self.reviews_dict, orient='index', columns=['Review', 'Rating'])
        df = df.rename_axis('Review_ID')
        return df

    def save_reviews_df(self, filename: str) -> None:
        df = self.get_reviews_df()

        df.to_csv(filename)



# for debugging purpose only
if __name__ == '__main__':
    URL = '''
        https://www.amazon.in/MSI-GeForce-Ventus-128-bit-Graphic/dp/B0C7W8GZMJ?dib=eyJ2IjoiMSJ9.VsRvMn0rzqVTPaeM1cWo332WcObX2BiFBJ_C_RodmqFcMcWvyc-SvyMeDJqAcDXdAIELk5YEg2XHb-Nq5Onk4cr7xRoR8P2g1-FoApNvokAaiidEQA1oYyThUm7GDQJ39opzqgi95NebcFhg6uRH8g-kqjQZ7PUt1f8rRqZJ2Ses9ZTyDbzD_eQul6CTgfh1IyI_NgLCEmCGogj3ycI0dR776f1D_BHz2KNv0wd2Rpo.DcSOxvnmWNzuDziIr7U8z_BcjfML8fITJuiOKFTSuOw&dib_tag=se&keywords=graphic%2Bcards&qid=1735564436&sr=8-8&th=1
    '''

    scraper = AmazonScraper()
    reviews = scraper.scrape(URL)
    print(scraper.get_reviews_df())
    scraper.save_reviews_df('reviews.csv')
