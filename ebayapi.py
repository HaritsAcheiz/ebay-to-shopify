from httpx import Client, AsyncClient
import asyncio
from dataclasses import dataclass
from urllib.parse import urljoin
from os import getenv
from dotenv import load_dotenv
import json
import base64
from urllib.parse import quote
import logging
from math import ceil

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class EbayAPI():
    api_base_url: str = 'https://api.ebay.com'
    ebay_access_token: str = None
    proxy_url: str = getenv('PROXY_URL')

    # Authentication
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
        with Client(proxy=self.proxy_url, follow_redirects=True) as client:
            response = client.get(endpoint, params=params)

        return response

    def access_token(self):
        client_id = getenv('CLIENT_ID')
        client_secret = getenv('CLIENT_SECRET')

        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

        url = "https://api.ebay.com/identity/v1/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_credentials}"
        }
        data = {
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope"
        }

        with Client(proxy=self.proxy_url) as client:
            response = client.post(url, headers=headers, data=data)

        return response

    # Read
    def search(self, q, limit=25, offset=0):
        logger.info(f'Fetching {(q, limit, offset)}...')
        endpoint = urljoin(self.api_base_url, '/buy/browse/v1/item_summary/search')

        headers = {
            'Authorization': f"Bearer {self.ebay_access_token}",
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
        }

        params = {
            'q': q,
            'limit': limit,
            'offset': offset
        }

        with Client(proxy=self.proxy_url, headers=headers) as client:
            response = client.get(endpoint, params=params)

        logger.info(f'Fetching {(q, limit, offset)}...Completed!')

        return response

    async def asearch(self, aclient, q, sem_limit, limit=25, offset=0):
        logger.info(f'Fetching {(q, limit, offset)}...')
        endpoint = urljoin(self.api_base_url, '/buy/browse/v1/item_summary/search')

        params = {
            'q': q,
            'limit': limit,
            'offset': offset
        }

        async with sem_limit:
            response = await aclient.get(endpoint, params=params, follow_redirects=True)
            if sem_limit.locked():
                await asyncio.sleep(1)
                response.raise_for_status()
        logger.info(f'Fetching {(q, limit, offset)}...Completed!')

        respone_json = response.json()
        itemSummaries = respone_json['itemSummaries']

        return itemSummaries

    async def search_all(self, results_counts, q, limit, nsem_limit):
        headers = {
            'Authorization': f"Bearer {self.ebay_access_token}",
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
        }

        sem_limit = asyncio.Semaphore(nsem_limit)

        offsets = [i for i in range(0, results_counts, limit)]

        tasks = []
        async with AsyncClient(proxy=self.proxy_url, headers=headers, timeout=120) as aclient:
            for offset in offsets:
                task = asyncio.create_task(self.asearch(aclient, q=q, sem_limit=sem_limit, limit=limit, offset=offset))
                tasks.append(task)
            itemSummaries = await asyncio.gather(*tasks)

        product_datas = []
        for item in itemSummaries:
            product_datas.extend(item)

        return product_datas

    def product(self, product_id):
        endpoint = urljoin(self.api_base_url, f'/buy/browse/v1/item/{product_id}')
        headers = {
            'Authorization': f"Bearer {self.ebay_access_token}",
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
        }

        with Client(headers=headers) as client:
            response = client.get(endpoint)

        return response

    async def aproduct(self, aclient, product_id, sem_limit):
        logger.info(f'Fetching {product_id}...')
        endpoint = urljoin(self.api_base_url, f'/buy/browse/v1/item/{product_id}')

        async with sem_limit:
            response = await aclient.get(endpoint, follow_redirects=True)
            if sem_limit.locked():
                await asyncio.sleep(1)
                response.raise_for_status()
        logger.info(f'Fetching {product_id}...Completed!')

        return response.json()

    async def all_products(self, product_ids, nsem_limit):
        headers = {
            'Authorization': f"Bearer {self.ebay_access_token}",
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
        }

        sem_limit = asyncio.Semaphore(nsem_limit)

        tasks = []
        async with AsyncClient(headers=headers, timeout=120) as aclient:
            for product_id in product_ids:
                task = asyncio.create_task(self.aproduct(aclient, product_id, sem_limit=sem_limit))
                tasks.append(task)
            product_details = await asyncio.gather(*tasks)

        return product_details


if __name__ == "__main__":
    eapi = EbayAPI()
    # ======================== configure_consent_request =============================
    # response = eapi.configure_consent_request()

    # ======================== get access_token =============================
    response = eapi.access_token()
    response_json = response.json()
    access_token = response_json['access_token']
    eapi.ebay_access_token = access_token

    # ========================  search items =============================
    response = eapi.search('drone', 3)

    # ======================== get product =============================
    # response = eapi.product('v1|286067196927|588169254194')

    # ======================== display =============================
    print(response)
    print(response.json())

    # ======================== playground =============================
    # offsets = []
    # limit = 250
    # results_counts = 7215
    # for i in range(0, results_counts, limit):
    #     offsets.append(i)

    # offsets = [i for i in range(0, results_counts, limit)]
    # print(offsets)
