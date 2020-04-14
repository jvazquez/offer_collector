import asyncio
import collections
import logging
import os

from typing import Any, Dict, List

import aiohttp
import feedparser
import pandas as pd

from dateutil.parser import parse
from motor.motor_asyncio import AsyncIOMotorClient

from config.collector import CollectorConfig
from utils.basic_loging_configuration import initialize_logging

initialize_logging()
STORAGE = os.getenv('STORAGE', 'mongodb://localhost:27017')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'feeds')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'collected_feeds')


async def store_with_database(data: List, options: Dict):
    try:
        client = AsyncIOMotorClient(STORAGE)
        database = client[DATABASE_NAME]
        collection = database[COLLECTION_NAME]

        clean_records = list()
        for entry in data:
            record = {key: value for key, value in entry.items()
                      if key not in options['excluded_fields']}
            record['published'] = parse(record['published'])
            clean_records.append(record)

        results = await collection.insert_many(clean_records)
        logging.info(f"Result of insert operation {results.inserted_ids}")
    except Exception:
        logging.exception("Problem with motor")


def get_translated(mapped_fields, field, real_header):
    translated = None
    if field in mapped_fields.keys():
        translated = mapped_fields.get(field)
    elif field in real_header:
        translated = field
    return translated


async def store_with_file(data: List, options: Dict):
    sane_headers = options.get("output_header")
    mapped_fields = options.get("mappings")
    sanitized_entries = list()
    index_map = {v: i for i, v in enumerate(sane_headers)}

    for raw_entry in data:
        clean_entry = dict()
        for raw_title, value in raw_entry.items():
            clean_title = get_translated(mapped_fields, raw_title, sane_headers)
            if clean_title is not None:
                if len(value) > 0:
                    if clean_title == 'tags':
                        clean_value = ",".join([data.get("term")
                                                for data in value])
                    else:
                        clean_value = value
                    clean_entry.update({clean_title: clean_value})
        clean_entry = {x: y
                       for x, y in
                       sorted(clean_entry.items(),
                              key=lambda pair: index_map[pair[0]])
                       }
        sanitized_entries.append(clean_entry)

    writer = pd.ExcelWriter("offers.xlsx", engine='xlsxwriter')
    pd.DataFrame(sanitized_entries).to_excel(writer,
                                             sheet_name="Offers")
    reports = collections.Counter(map(lambda x: x.get("company"),
                                      sanitized_entries))
    pd.DataFrame(reports.items()).to_excel(writer, sheet_name="Reports")
    writer.save()
    writer.close()


async def store(data: List, options: Dict):
    """
    Send the obtained data to the storage microservice via socket

    :param data:
    :param options:
    :return:
    """
    logging.info(f'Will store using {options.get("storage")}')
    if options.get("storage") == "csv":
        await store_with_file(data, options)
    else:
        await store_with_database(data, options)


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


async def fetch_rss_feeds(main_loop: asyncio.AbstractEventLoop,
                          configuration: Dict):
    """
    Iterate over the list of known feeds and extract information

    :param main_loop:
    :param configuration:
    :return:
    """
    storage = []
    async with aiohttp.ClientSession(loop=main_loop) as session:
        for feed in configuration.get("feeds"):
            html = await fetch(session, feed.get('url'))
            data = await main_loop.run_in_executor(None, parse_rss, html)
            storage += data.get("entries")

        await store(storage, configuration.get("parseOptions"))

if __name__ == '__main__':
    config_collector = CollectorConfig()
    config_collector.load_config()
    loop = asyncio.get_event_loop()
    loop.set_debug(config_collector.config.get("debug"))
    loop.run_until_complete(fetch_rss_feeds(loop,
                                            config_collector.config)
                            )
    loop.stop()
