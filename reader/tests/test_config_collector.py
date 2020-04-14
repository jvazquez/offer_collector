import os
import unittest

from pathlib import Path

from reader.config.collector import CollectorConfig


class TestConfigCollector(unittest.TestCase):
    def test_init_uses_default(self):
        collector_config = CollectorConfig()
        expected = Path("feeds.json")
        self.assertEqual(expected, collector_config.configuration_file)

    def test_init_uses_env(self):
        os.environ["ALTERNATIVE_CONFIGURATION"] = "fake.json"
        collector_config = CollectorConfig()
        expected = Path("fake.json")
        self.assertEqual(os.getenv("ALTERNATIVE_CONFIGURATION"), "fake.json")
        self.assertEqual(expected, collector_config.configuration_file)
        del os.environ["ALTERNATIVE_CONFIGURATION"]

    def test_load_with_default(self):
        collector_config = CollectorConfig()
        collector_config.load_config()
        self.assertIn("feeds", collector_config.config.keys())
        self.assertIn("parseOptions", collector_config.config.keys())


if __name__ == '__main__':
    unittest.main()
