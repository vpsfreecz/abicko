import os
import re
from lxml import html
from urllib.request import urlretrieve

import logging
logging.basicConfig(level=logging.INFO, style="{", format="{message}")
log = logging.getLogger("webscrape")

base_download = "cache"

re_target_replace = re.compile("[^a-z]")


class Object:
    base_url = ""

    @property
    def url(self):
        return self.base_url + self._path

    @property
    def target(self):
        return os.path.join(base_download, re_target_replace.sub("_", self._path.lstrip("/")))

    def download(self):
        log.info("Downloading {!r} to {!r}".format(self.url, self.target))
        os.makedirs(base_download, exist_ok=True)
        urlretrieve(self.url, self.target)


class List(Object):
    # xpath_item = ...

    def parse(self):
        with open(self.target) as stream:
            root = html.fromstring(stream.read())
        return self.parse_root(root)

    def parse_root(self, root):
        sections = root.xpath(self.xpath_item)
        result = [self.parse_section(section) for section in sections]
        log.info("List items: {}".format(result))
        return result

    def parse_section(self, section):
        return section.text_content().strip()
