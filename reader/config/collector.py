import json
import os

from pathlib import Path


class CollectorConfig:
    def __init__(self):
        self.config = None
        configuration_file = os.getenv("ALTERNATIVE_CONFIGURATION", None)
        if configuration_file is None:
            self.configuration_file = Path(Path(__file__).parent, "feeds.json")

    def load_config(self):
        with open(self.configuration_file) as config_file:
            self.config = json.loads(config_file.read())
