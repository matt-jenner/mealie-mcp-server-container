from __future__ import annotations

import os
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path


def fetch_upstream(repo: str, ref: str, destination: Path) -> None:
    url = f"{repo.rstrip('/')}/archive/{ref}.tar.gz"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        archive_path = tmp_path / "source.tar.gz"
        extract_path = tmp_path / "extract"
        extract_path.mkdir()

        urllib.request.urlretrieve(url, archive_path)

        with tarfile.open(archive_path, "r:gz") as archive:
            archive.extractall(extract_path, filter="data")

        entries = list(extract_path.iterdir())
        if len(entries) != 1:
            raise RuntimeError(f"Expected one archive root directory, found {len(entries)}")

        shutil.rmtree(destination, ignore_errors=True)
        shutil.copytree(entries[0], destination)


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("Usage: fetch_upstream.py <repo> <ref> <destination>")

    repo, ref, destination = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    fetch_upstream(repo, ref, destination)


if __name__ == "__main__":
    main()
