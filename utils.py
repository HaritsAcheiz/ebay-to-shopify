import pandas as pd
import json


def parse_search_response(search_response_json):
	records = search_response_json['itemSummaries']
	df = pd.DataFrame.from_records(records)

	return df


def records_to_df(records):
	df = pd.DataFrame.from_records(records)

	return df


def get_product_ids(filepath):
	df = pd.read_csv(filepath)
	product_ids = df['itemId'].to_list()

	return product_ids


def transform_data(products_filepath, details_filepath):
	# Create shopify tamplate
	with open('shopify_schema.json', 'r') as file:
		product_schema = json.load(file)
	df_shopify = pd.DataFrame([product_schema])

	# Read Source
	df_products = pd.read_csv(products_filepath)
	df_details = pd.read_csv(details_filepath)
	df_products_details = df_products.merge(df_details, how='left', on='itemId')

	# Mapping
	df_shopify['Handle'] = df_products_details['']
	df_shopify['Title'] = df_products_details['title']
	df_shopify['Body (HTML)'] = df_products_details['description']



if __name__ == '__main__':
	transform_data()
