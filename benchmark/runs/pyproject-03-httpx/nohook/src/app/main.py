import asyncio

import httpx

URLS = [
    "https://httpbin.org/get",
    "https://httpbin.org/uuid",
    "https://httpbin.org/ip",
]


async def fetch(client: httpx.AsyncClient, url: str) -> httpx.Response:
    response = await client.get(url)
    response.raise_for_status()
    return response


async def main() -> None:
    async with httpx.AsyncClient() as client:
        responses = await asyncio.gather(*(fetch(client, url) for url in URLS))
    for url, response in zip(URLS, responses):
        print(url, response.status_code, response.json())


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
