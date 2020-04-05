import asyncio
import logging
import os

from typing import Dict, List

import aiohttp
import feedparser

from dateutil.parser import parse
from motor.motor_asyncio import AsyncIOMotorClient

from utils.basic_loging_configuration import initialize_logging

initialize_logging()
SITES = [{
        'url': 'http://stackoverflow.com/jobs/feed?r=true',
        'name': 'StackOverflow',
    },
    {
        'url': 'https://remoteok.io/remote-jobs.rss',
        'name': 'RemoteOk'
    },
]
STORAGE = os.getenv('STORAGE', 'mongodb://localhost:27017')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'feeds')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'collected_feeds')
DEBUG = True if os.getenv('DEBUG') is not None else False
INTERVAL = int(os.getenv('INTERVAL', 60))
EXCLUDE_FIELDS = ['published_parsed',
                  'summary_detail',
                  'updated_parsed',
                  'title_detail',
                  'links',
                  'id']


async def store(data: List):
    """
    Send the obtained data to the storage microservice via socket

    :param data:
    :return:
    """
    try:
        client = AsyncIOMotorClient(STORAGE)
        database = client[DATABASE_NAME]
        collection = database[COLLECTION_NAME]

        clean_records = list()
        for entry in data.get('entries'):
            record = {key: value for key, value in entry.items()
                      if key not in EXCLUDE_FIELDS}
            record['published'] = parse(record['published'])
            if record.get('updated'):
                record['updated'] = parse(record['updated'])
            clean_records.append(record)

        results = await collection.insert_many(clean_records)
        logging.info(f"Result of insert operation {results.inserted_ids}")
    except Exception:
        logging.exception("Problem with motor")
    finally:
        return True


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
    loop.run_until_complete(fetch_rss_feeds(loop, SITES))
    # TODO When this is deployed, I'll scan daily so add optparse
    # or perhaps an asyncserver that listens to authenticated requests?
    # loop.create_task(job_fetch(INTERVAL, loop))
    # loop.run_forever()
    # loop.close()
    loop.stop()
