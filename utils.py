import pandas as pd
from dataclasses import dataclass


@dataclass
class oAuth_token():
	access_token: str = None
	token_expiry: str = None
	refresh_token: str = None
	refresh_token_expiry: str = None
	error: str = None


def parse_search_response(search_response_json):
	records = search_response_json['itemSummaries']
	df = pd.DataFrame.from_records(records)
	return df


def generate_request_headers(client_id, client_secret):


	return headers