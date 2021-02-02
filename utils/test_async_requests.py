import aiohttp
import asyncio
import json

from pprint import pprint


async def fetch_tickers(session, url):
    async with session.get(url=url, params=None) as response:
        http_response = await response.text()
        http_response = json.loads(http_response)
        return http_response

async def main():
    urls = []
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks.append(fetch_tickers(session, url))
        ref_data = await asyncio.gather(*tasks, return_exceptions=True)
        print(ref_data)


if __name__ == '__main__':
    loop = asyncio.get_event_loop().run_until_complete(main())
