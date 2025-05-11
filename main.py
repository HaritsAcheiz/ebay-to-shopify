from ebayapi import EbayAPI
from utils import *
import asyncio

if __name__ == '__main__':
    eapi = EbayAPI()

    # Authentication
    response = eapi.access_token()
    response_json = response.json()
    access_token = response_json['access_token']
    eapi.ebay_access_token = access_token

    # get results_counts
    # q = 'gas scooters'
    # search_response = eapi.search(q=q)
    # search_response_json = search_response.json()
    # results_counts = search_response_json['total']
    # results_counts_test = 500

    # Get product datas
    # records_product = asyncio.run(eapi.search_all(results_counts=results_counts_test, q=q, limit=200, nsem_limit=4))
    # df_products = records_to_df(records_product)
    # df_products.to_csv('data/gas_scooter_search_result.csv', index=False)

    # Get product details
    # product_ids = get_product_ids('data/gas_scooter_search_result.csv')
    # records_product_details = asyncio.run(eapi.all_products(product_ids[0:10], 4))
    # df_product_details = records_to_df(records_product_details)
    # df_product_details.to_csv('data/gas_scooter_products.csv', index=False)

    # Convert to Shopify
    df_shopify = transform_data('data/gas_scooter_search_result.csv', 'data/gas_scooter_products.csv')
    df_shopify.to_csv('import_products.csv', index=False)
