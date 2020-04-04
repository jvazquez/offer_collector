import asyncio
import datetime
import json
import logging
import os

import aiohttp
import feedparser
import socketio

from typing import Dict, List

from sandbox.basic_loging_configuration import initialize_logging

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

STORAGE = os.getenv('STORAGE', 'http://localhost:3000')
DEBUG = True if os.getenv('DEBUG') is not None else False
INTERVAL = int(os.getenv('INTERVAL', 60))


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


async def store(data: List):
    """
    Send the obtained data to the storage microservice via socket

    :param data:
    :return:
    """
    sio = socketio.AsyncClient()
    logging.info(f"Connecting to {STORAGE}")
    await sio.connect(STORAGE)
    await sio.emit(
        "python-message",
        json.dumps(data.get('entries'),
                   default=json_serial)
    )


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    """
    Async http get to a feed

    :param session:
    :param url:
    :return:
    """
    async with session.get(url) as response:
        return await response.text()


def parse_rss(html: str) -> List[Dict]:
    """
    Use feedparser package to translate the feed
    to json

    :param html: str
    :return: List[Dict]
    """
    return feedparser.parse(html)


async def fetch_rss_feeds(main_loop: asyncio.AbstractEventLoop, sites: Dict):
    """
    Iterate over the list of known feeds and extract information

    :param main_loop:
    :param sites:
    :return:
    """

    async with aiohttp.ClientSession(loop=main_loop) as session:
        for feed in sites:
            html = await fetch(session, feed.get('url'))
            rss_list = await main_loop.run_in_executor(None, parse_rss, html)
            await store(rss_list)


async def job_fetch(interval: int, main_loop: asyncio.AbstractEventLoop):
    while True:
        try:
            main_loop.create_task(fetch_rss_feeds(main_loop, SITES))
            await asyncio.sleep(interval, loop=main_loop)
        except asyncio.CancelledError:
            logging.info("Received cancel signal")

    main_loop.stop()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.set_debug(DEBUG)
    loop.create_task(job_fetch(INTERVAL, loop))
    loop.run_forever()
    loop.close()
