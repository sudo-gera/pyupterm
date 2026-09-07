import urllib.request
import dataclasses
import typing
import json
import pathlib
import datetime

import cache

@dataclasses.dataclass
class _OneDownloader:
    current_cache: cache.ICache

    def download_bytes(self, url: str) -> bytes:
        if url in self.current_cache:
            return self.current_cache[url]
        with urllib.request.urlopen(url) as request:
            data = typing.cast(bytes, request.read())
        self.current_cache[url] = data
        return data

    def download_str(self, url: str) -> str:
        return self.download_bytes(url).decode()

    def download_json(self, url: str) -> typing.Any:
        return json.loads(self.download_str(url))

@dataclasses.dataclass
class _Downloader:
    permanent: _OneDownloader
    temporary: _OneDownloader

class Downloader(_Downloader):
    
    def __init__(self, dir: pathlib.Path) -> None:
        perm_cache = cache.Cache(dir)
        temp_cache = cache.TTLCache(perm_cache, datetime.timedelta(seconds=3600))
        super().__init__(
            permanent=_OneDownloader(perm_cache),
            temporary=_OneDownloader(temp_cache),
        )

