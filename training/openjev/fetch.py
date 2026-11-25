"""Fetch a pinned public snapshot with restartable ranged reads, then verify all files."""

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import time
from urllib.request import Request, urlopen

from flash import MANIFEST_HASH, MODEL, MODEL_ID, REVISION, sha, verify_model

BASE_URL = f"https://huggingface.co/{MODEL_ID}/resolve/{REVISION}/"
BLOCK = 16 * 1024**2


def fetch_range(item):
    url, part, start, end, size = item
    length = end - start + 1
    if part.is_file() and part.stat().st_size == length:
        return
    temp = part.with_suffix(".partial")
    for attempt in range(6):
        try:
            request = Request(f"{url}?start={start}", headers={"Range": f"bytes={start}-{end}"})
            with urlopen(request, timeout=60) as source, temp.open("wb") as out:
                if source.headers.get("Content-Range") != f"bytes {start}-{end}/{size}":
                    raise ValueError("Server did not honor byte range")
                shutil.copyfileobj(source, out, 1024**2)
            if temp.stat().st_size != length:
                raise OSError("Short range response")
            temp.replace(part)
            return
        except (OSError, ValueError):
            if attempt == 5:
                raise
            time.sleep(min(2**attempt, 10))


def fetch(name, meta):
    dest = MODEL / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size == meta["bytes"] and sha(dest) == meta["sha256"]:
        return
    url = BASE_URL + name
    temp = dest.with_suffix(".assembling")
    if meta["bytes"] < BLOCK:
        with urlopen(url, timeout=60) as src, temp.open("wb") as out:
            shutil.copyfileobj(src, out)
    else:
        size = meta["bytes"]
        parts = MODEL / ".parts" / name
        parts.mkdir(parents=True, exist_ok=True)
        jobs = [(url, parts / f"{i:05}.bin", start, min(start+BLOCK, size)-1, size)
                for i, start in enumerate(range(0, size, BLOCK))]
        with ThreadPoolExecutor(max_workers=6) as pool:
            for i, _ in enumerate(pool.map(fetch_range, jobs), 1):
                if i % 32 == 0:
                    print(f"{name}: {i}/{len(jobs)} ranges ready", flush=True)
        with temp.open("wb") as out:
            for _, part, *_ in jobs:
                with part.open("rb") as src:
                    shutil.copyfileobj(src, out, 1024**2)
    if sha(temp) != meta["sha256"]:
        raise ValueError(f"Digest mismatch: {name}. Retain partials for diagnosis.")
    temp.replace(dest)
    if meta["bytes"] >= BLOCK:
        for _, part, *_ in jobs:
            part.unlink()
    print(f"Verified {name}", flush=True)


if __name__ == "__main__":
    MODEL.mkdir(parents=True, exist_ok=True)
    with urlopen(BASE_URL + "MANIFEST.json", timeout=60) as response:
        raw = response.read()
    if hashlib.sha256(raw).hexdigest() != MANIFEST_HASH:
        raise ValueError("Unexpected upstream manifest")
    (MODEL / "MANIFEST.json").write_bytes(raw)
    entries = json.loads(raw)
    for name, entry in entries.items():
        if not name.startswith(("assets/", "_")) and name != "helper/shim_mlx.py":
            fetch(name, entry)
    verify_model()
