from httpx import Client
from dataclasses import dataclass
from urllib.parse import urljoin
from os import getenv
from dotenv import load_dotenv
import ebayoauth
from ebayoauth.oauthclient.oauth2api import oauth2api
from ebayoauth.oauthclient.model.model import environment

load_dotenv()


@dataclass
class EbayAPI():
    api_base_url: str = 'https://api.ebay.com'

    def access_token(self):
        oauthapi = oauth2api()
        scopes = ['https://api.ebay.com/oauth/api_scope']
        auth_url = oauthapi.generate_user_authorization_url(environment.Production, scopes)

        return auth_url

    def search(self, q, limit=25, offset=0):
        endpoint = urljoin(self.api_base_url, '/buy/browse/v1/item_summary/search')
        headers = {
            'Authorization': f"Bearer {getenv('EBAY_OAUTH_TOKEN')}",
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
    response = eapi.access_token()
    # response = eapi.search('drone', 3)
    # response = eapi.product('v1%7C145450205843%7C0')

    print(response)
    # print(response.json())
