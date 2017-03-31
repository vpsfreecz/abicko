import os
import sys
import argparse
import re
import datetime
from lxml import html
from urllib.request import urlretrieve

base_url = "https://www.abclinuxu.cz"
base_download = "cache"

re_target_replace = re.compile("[^a-z]")

class Object:
    @property
    def url(self):
        return base_url + self._path

    @property
    def target(self):
        return os.path.join(base_download, re_target_replace.sub("_", self._path.lstrip("/")))

    def download(self):
        os.makedirs(base_download, exist_ok=True)
        urlretrieve(self.url, self.target)


class Blog(Object):
    re_url = re.compile("^.*/blog/([^/]*)$")

    def __init__(self, name):
        self._name = name
        self._path = "/blog/" + name

    def __repr__(self):
        return "<{} name={}>".format(type(self).__name__, self.name)

    def parse(self):
        with open(self.target) as stream:
            root = html.fromstring(stream.read())
        return self.parse_root(root)

    def parse_root(self, root):
        sections = root.xpath("//div[@id='st']/div[@class='cl']")
        return [self.parse_section(section) for section in sections]

    def parse_section(self, section):

        headline = section.xpath("./h2")[0]
        meta = section.xpath("./p[@class='meta-vypis']")[0]

        section.remove(headline)
        section.remove(meta)

        # TODO: We might want to return ordered dictionary for nicer output
        return dict([
            ("headline", headline.text_content().strip()),
            ("date", self.parse_date(meta.text.strip().split("\n")[0])),
            ("category", meta.xpath("./a")[0].text),
            ("lead", section.text_content().strip()),
        ])

    def parse_date(self, date):
        formats = "%d.%m.%Y %H:%M", "%d.%m. %H:%M"
        for fmt in formats:
            try:
                timestamp = datetime.datetime.strptime(date, fmt)
            except ValueError:
                continue
            return timestamp.strftime("%Y-%m-%d %H:%M:%S")
        raise ValueError("Unknown date format: {} (supported formats: {})".format(date, ", ".join(repr(fmt) for fmt in formats)))


def get(url):
    registered_classes = [Blog]

    for cls in registered_classes:
        match = cls.re_url.match(url)
        if match:
            return cls(*match.groups())

    raise ValueError("Unknown url: {!r}.".format(url))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("url")
    options = parser.parse_args()

    item = get(options.url)

    if options.command == 'whatis':
        print(item)
    elif options.command == 'download':
        item.download()
    elif options.command == 'parse':
        import yaml
        yaml.safe_dump(
            item.parse(),
            stream=sys.stdout,
            allow_unicode=True,
            default_flow_style=False)
