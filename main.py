from ebayapi import EbayAPI
from utils import *

if __name__ == '__main__':
    ebayapi = EbayAPI()
    # search_response = ebayapi.search('gas scooters')
    # search_df = parse_search_response(search_response.json())

    search_df.to_csv('data/search_result.csv')

    product_ids = search_df['itemId'].to_list()
    product_detail_records = []
    for product_id in product_ids:
        response = ebayapi.product(product_id)

