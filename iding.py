from urllib.parse import urlsplit
from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument('ids', nargs='+')

urls = parser.parse_args().ids
ids = [urlsplit(u).path.strip('/track/') for u in urls]

for id in ids:
    print(id)