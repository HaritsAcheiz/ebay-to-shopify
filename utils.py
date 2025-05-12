import pandas as pd
import json
import re
import ast


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


def to_handle(title):
	if (pd.isna(title)) | (title == 0):
		result = None
	else:
		title.replace('-', '')
		pattern = re.compile(r"\b[a-zA-Z0-9]+\b")
		matches = pattern.findall(title.lower().strip())
		result = '-'.join(matches)

	return result


def generate_category(category_path):
	if pd.isna(category_path):
		result = None
	else:
		category_list = category_path.split('|')
		result = ' > '.join(category_list)

	return result


def to_tags(categoryPath):
	if (categoryPath == '') | pd.isna(categoryPath):
		result = ''
	else:
		result = categoryPath.replace('|', ',')

	return result


def generate_option_name(option_value, option_name):
	if (option_value == '') | pd.isna(option_value):
		result = ''
	else:
		result = option_name

	return result


def generate_SKU(sku_log_filepath, product_type, color, size):
	try:
		try:
			df = pd.read_csv(sku_log_filepath)
			last_no = df.iloc[-1]['No']
			counter = int(last_no) + 1
		except (FileNotFoundError, IndexError):
			counter = 1
			df = pd.DataFrame(columns=['No', 'SKU'])

		new_sku = f"#{product_type}-{counter:04d}"
		if (pd.isna(color) | (color == '')):
			pass
		else:
			new_sku = new_sku + f"-{color}"
		if (pd.isna(size) | (size == '')):
			pass
		else:
			new_sku = new_sku + f"-{size}"
		new_row = pd.DataFrame({'No': [counter], 'SKU': [new_sku]})
		df = pd.concat([df, new_row], ignore_index=True)
		df.to_csv(sku_log_filepath, index=False)
		return new_sku

	except Exception as e:
		raise Exception(f"Error generating SKU: {str(e)}")


def get_inventory_qty(estimated_availability):
	if (estimated_availability == '') | pd.isna(estimated_availability):
		result = ''
	else:
		data = ast.literal_eval(estimated_availability)
		inventory_qty = data[0]['estimatedRemainingQuantity']
		result = inventory_qty

	return result


def get_compare_at_price(marktingPrice):
	if (marktingPrice == '') | pd.isna(marktingPrice):
		result = ''
	else:
		data = ast.literal_eval(marktingPrice)
		compare_at_price = data['originalPrice']['value']
		result = compare_at_price

	return result


def get_price(price):
	if (price == '') | pd.isna(price):
		result = ''
	else:
		data = ast.literal_eval(price)
		price_value = data['value']
		result = price_value

	return result


def transform_data(products_filepath, details_filepath):
	# Create shopify tamplate
	with open('shopify_schema.json', 'r') as file:
		product_schema = json.load(file)
	df_shopify = pd.DataFrame([product_schema])
	df_shopify = df_shopify[0:0]

	# Read Source
	df_products = pd.read_csv(products_filepath)
	df_details = pd.read_csv(details_filepath)
	df_products_details = df_products.merge(df_details, how='inner', on='itemId')
	print(df_products_details.columns)

	# Mapping
	df_shopify['Handle'] = df_products_details['title_x'].apply(to_handle)
	df_shopify['Title'] = df_products_details['title_x']
	df_shopify['Body (HTML)'] = df_products_details['description']
	df_shopify['Vendor'] = df_products_details['brand']
	df_shopify['Product Category'] = df_products_details.apply(lambda x: generate_category(x['categoryPath']), axis=1)
	df_shopify['Type'] = 'Costumes'
	df_shopify['Tags'] = df_products_details['categoryPath'].apply(to_tags)
	df_shopify['Published'] = True
	df_shopify['Option1 Name'] = df_products_details.apply(lambda x: generate_option_name(x['color'], 'Color'), axis=1)
	df_shopify['Option1 Value'] = df_products_details['color']
	df_shopify['Option2 Name'] = df_products_details.apply(lambda x: generate_option_name(x['size'], 'Size'), axis=1)
	df_shopify['Option2 Value'] = df_products_details['size']
	df_shopify['Option3 Name'] = ''
	df_shopify['Option3 Value'] = ''
	df_shopify['Variant SKU'] = df_products_details.apply(lambda x: generate_SKU('sku_log.csv', 'GSC', x['color'], x['size']), axis=1)
	df_shopify['Variant Grams'] = ''
	df_shopify['Variant Inventory Tracker'] = 'shopify'
	df_shopify['Variant Inventory Qty'] = df_products_details['estimatedAvailabilities'].apply(get_inventory_qty)
	df_shopify['Variant Inventory Policy'] = 'deny'
	df_shopify['Variant Inventory Fulfillment Service'] = 'manual'
	df_shopify['Variant Price'] = df_products_details['price_x'].apply(get_price)
	df_shopify['Variant Compare At Price'] = df_products_details['marketingPrice_x'].apply(get_compare_at_price)
	df_shopify['Variant Requires Shipping'] = True
	df_shopify['Variant Taxable'] = True
	# df_shopify['Variant Barcode'] = df_products_details['Selling Unit Master UPC']

	df_shopify.to_csv('data/cek.csv', index=False)


if __name__ == '__main__':
	transform_data('data/gas_scooter_search_result.csv', 'data/gas_scooter_products.csv')
	# generate_SKU('sku_log.csv')
