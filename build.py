#!/usr/bin/env python3
from __future__ import annotations
import pathlib
import argparse
import os
import typing
import json
import pprint
import dataclasses
import tarfile
import io
import tempfile
import subprocess
import shutil

import download
import structs

this_file = pathlib.Path(__file__).resolve()
repo_root = this_file.parent

def main(tag_name: str) -> None:
    loader = download.Downloader(repo_root / '.cache')
    releases_json = loader.temporary.download_json(f'https://api.github.com/repos/owenthereal/upterm/releases')
    releases = [
        structs.release_info(
            **{
                key :(
                    [
                        structs.asset_info(
                            **asset_json
                        )
                        for asset_json in value
                    ]
                    if key == 'assets' else
                    value
                )
                for key, value in release_json.items()
            }
        )
        for release_json in releases_json
    ]

    matching_releases = [
        release
        for release in releases
        if release.tag_name == tag_name
    ]

    if len(matching_releases) > 1:
        raise ValueError(f"Too many releases with this tag")

    if len(matching_releases) < 1:
        raise ValueError(f"Given {tag_name = !r} is not in {[release.tag_name for release in releases]}")

    release = matching_releases[0]

    files: list[structs.file_info] = []

    for asset in release.assets:
        if asset.name.endswith('.tar.gz'):
            *app_chunks, os, arch = asset.name.removesuffix('.tar.gz').split('_')
            if app_chunks == ['upterm']:
                files.append(
                    structs.file_info(
                        os=os,
                        arch=arch,
                        url=asset.browser_download_url,
                        name=asset.name,
                    )
                )

    build_root = repo_root / '.build'
    shutil.rmtree(build_root, ignore_errors=True)
    build_root.mkdir(parents=True, exist_ok=True)
    package_root = build_root / 'pyupterm'
    shutil.copytree(repo_root / 'skel' / 'pyupterm', package_root)

    for file in files:
        data = loader.permanent.download_bytes(file.url)
        bytes_io = io.BytesIO(data)
        print(f"{file.os = } {file.arch = }", flush=True)
        with tarfile.open(fileobj=bytes_io, mode="r") as tar:
            for member in tar:
                if member.isfile():
                    if member.name.startswith('etc/man/'):
                        pass
                    elif member.name.startswith('etc/completion/'):
                        pass
                    elif member.name.endswith('.md'):
                        pass
                    elif member.name == 'LICENSE':
                        pass
                    else:
                        # print(f"Processing: {member.name} ({member.size} bytes)")
                        with tempfile.NamedTemporaryFile(mode='wb', delete=True) as temp_file:
                            if fp := tar.extractfile(member):
                                temp_file.write(fp.read())
                                temp_file.flush()
                                for command in [
                                    ['file', temp_file.name],
                                    ['ldd', temp_file.name],
                                    ['readelf', '-l', temp_file.name],
                                ]:
                                    print(command)
                                    subprocess.run(command)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag-name', required=True)
    args = parser.parse_args()
    tag_name = typing.cast(str, args.tag_name)
    main(tag_name)

