import asyncio
import json
import logging

import aiohttp
import feedparser
import socketio

from typing import Dict, List

from basic_loging_configuration import initialize_logging

initialize_logging()
SITES = [{
        'url': 'http://stackoverflow.com/jobs/feed?r=true',
        'name': 'StackOverflow'
    },
    {
        'url': 'https://remoteok.io/remote-jobs.rss',
        'name': 'Remoteok'
    },
]


async def store(data: List, site: str):
    """

    :param data:
    :param site:
    :return:
    """
    python_offers = list(
        filter(
            lambda offer: 'python' not in offer.get('tags'), data.get('entries')
        )
    )
    sio = socketio.AsyncClient()
    await sio.connect('http://localhost:3000')
    await sio.emit("python-message", json.dumps(python_offers))

    # await sio.connect()
    # sio.emit("python-message", {"name": "foobert"})
    # logging.info(f"Python offers found: {len(python_offers)}")


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    """
    Async http get to a feed

    :param session:
    :param url:
    :return:
    """
    async with session.get(url) as response:
        return await response.text()


async def fetch_rss_feeds(loop: asyncio.AbstractEventLoop, feeds: Dict):
    """
    Iterate over the list of known feeds and extract information

    :param loop:
    :param feeds:
    :return:
    """

    for feed in feeds:
        async with aiohttp.ClientSession(loop=loop) as session:
            html = await fetch(session, feed.get('url'))
            rss = feedparser.parse(html)

            stored_records = await store(rss, feed.get('name'))
            logging.info(stored_records)


if __name__ == '__main__':
    logging.info("Starting")
    main_loop = asyncio.get_event_loop()
    main_loop.run_until_complete(
        fetch_rss_feeds(main_loop, SITES)
    )
