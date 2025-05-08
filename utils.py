import pandas as pd


def parse_search_response(search_response_json):
	records = search_response_json['itemSummaries']
	df = pd.DataFrame.from_records(records)
	return df