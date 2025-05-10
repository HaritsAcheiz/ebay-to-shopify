from httpx import Client
from dataclasses import dataclass
from urllib.parse import urljoin
from os import getenv
from dotenv import load_dotenv
import json
from utils import generate_request_headers
import base64
from urllib.parse import quote

load_dotenv()


@dataclass
class EbayAPI():
    api_base_url: str = 'https://api.ebay.com'
    ebay_access_token: str = None

    def configure_consent_request(self):
        endpoint = 'https://auth.ebay.com/oauth2/authorize'
        scope = 'https://api.ebay.com/oauth/api_scope'
        params = {
            'client_id': getenv('CLIENT_ID'),
            'locale': 'en-US',
            'redirect_uri': getenv('RU_NAME'),
            'response_type': 'code',
            'scope': quote(scope)
        }
        with Client(follow_redirects=True) as client:
            response = client.get(endpoint, params=params)

        return response

    def access_token(self):
        client_id = getenv('CLIENT_ID')
        client_secret = getenv('CLIENT_SECRET')

        # Encode credentials in Base64
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

        # Request token
        url = "https://api.ebay.com/identity/v1/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_credentials}"
        }
        data = {
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope"
        }

        with Client() as client:
            response = client.post(url, headers=headers, data=data)

        return response

    def search(self, q, limit=25, offset=0):
        endpoint = urljoin(self.api_base_url, '/buy/browse/v1/item_summary/search')
        headers = {
            'Authorization': f"Bearer {self.access_token}",
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
        }
        params = {
            'q': q,
            'limit': limit,
            'offset': offset
        }

        with Client(headers=headers) as client:
            response = client.get(endpoint, params=params)
            return response

    def product(self, product_id):
        endpoint = urljoin(self.api_base_url, f'/buy/browse/v1/item/{product_id}')
        headers = {
            'Authorization': f"Bearer {getenv('EBAY_OAUTH_TOKEN')}",
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
        }

        with Client(headers=headers) as client:
            response = client.get(endpoint)
            return response


if __name__ == "__main__":
    eapi = EbayAPI()
    # response = eapi.configure_consent_request()
    response = eapi.access_token()
    response_json = response.json()
    access_token = response_json['access_token']
    eapi.ebay_access_token = access_token

    # response = eapi.access_token()
    response = eapi.search('drone', 3)
    # response = eapi.product('v1%7C145450205843%7C0')

    print(response)
    print(response.json())
