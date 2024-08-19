#!/usr/bin/env python3

import json
from pathlib import Path
import requests
import hashlib
import logging

def sha256(file: Path) -> str:
    hash = hashlib.sha256()
    with file.open('rb') as f:
        for block in iter(lambda: f.read(4096), b""):
            hash.update(block)
    return hash.hexdigest()

def download(url: str) -> Path:
    file = Path(url.split('/')[-1])
    logging.info(f'downloading {url} to {file}')
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with file.open('wb') as f:
            chunk_count = 0
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
                chunk_count = chunk_count + 1
                logging.info(f'{chunk_count * 8} KiB')
    return file

def main():
    logging.basicConfig(level=logging.INFO)
    manifest_path = Path("org.freedesktop.Sdk.Extension.moonbit.json")
    with manifest_path.open('r') as f:
        manifest = json.load(f)
    if 'modules' not in manifest:
        return
    for module in manifest['modules']:
        if 'sources' not in module:
            continue
        for source in module['sources']:
            if 'url' not in source:
                continue
            file = download(source['url'])
            sha256sum = sha256(file)
            source['sha256'] = sha256sum
    with manifest_path.open('w') as f:
        f.write(json.dumps(manifest))

if __name__ == "__main__":
    main()
