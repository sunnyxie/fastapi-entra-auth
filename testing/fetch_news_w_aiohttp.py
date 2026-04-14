import aiohttp
import asyncio

# sample function using aiohttp (async programming)
async def fetch_top_headlines(category: str, api_key: str):
    params = {
                'category': category, 
                'token': api_key
              }
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get('https://finnhub.io/api/v11/news', params=params)
            response.raise_for_status()
            return await response.json()
    except Exception as e:
        print(f'fetch_top_headlines Error: {e}')
        return []
