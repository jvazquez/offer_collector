import asyncio
import logging

import aiohttp
import feedparser

from sandbox.basic_loging_configuration import initialize_logging
from sites import SITES

initialize_logging()
INTERVAL = 60


async def store(data):
    logging.info(f"Here I'll do something with data {data}")
    return {"inserted": 1, "filtered": 1}


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def fetchfeeds(loop, feedurls):
    feeds = []

    for url in feedurls:
        feeds.append(
            {
                'url': url,
                'last': ""
             }
        )

    for feed in feeds:
        async with aiohttp.ClientSession(loop=loop) as session:
            html = await fetch(session, feed['url'])
            rss = feedparser.parse(html)
            stored_records = await store(rss)
            logging.info(stored_records)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        fetchfeeds(loop, SITES)
    )
