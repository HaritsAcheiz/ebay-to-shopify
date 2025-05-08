from ebayapi import EbayAPI
from utils import *

if __name__ == '__main__':
    ebayapi = EbayAPI()
    search_response = ebayapi.search('gas scooters')
    search_df = parse_search_response(search_response.json())
    search_df.to_csv('data/search_result.csv')
