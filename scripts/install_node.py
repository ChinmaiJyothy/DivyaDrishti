"""Download and extract a portable Node.js into the project tools directory."""
from __future__ import annotations

import os
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path


NODE_VERSION = "v20.16.0"
DOWNLOAD_URL = f"https://nodejs.org/dist/{NODE_VERSION}/node-{NODE_VERSION}-win-x64.zip"


def install(root: Path) -> Path:
    tools = root / "tools"
    node_dir = tools / "node"
    if node_dir.exists() and (node_dir / "node.exe").exists():
        print(f"Node.js already installed at {node_dir}")
        return node_dir

    tools.mkdir(parents=True, exist_ok=True)
    zip_path = tools / f"node-{NODE_VERSION}-win-x64.zip"

    print(f"Downloading Node.js {NODE_VERSION} from {DOWNLOAD_URL} ...")
    urllib.request.urlretrieve(DOWNLOAD_URL, zip_path)
    print(f"Saved to {zip_path}")

    extract_to = tools / f"node-{NODE_VERSION}-win-x64"
    if extract_to.exists():
        shutil.rmtree(extract_to)
    print(f"Extracting to {tools} ...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(tools)

    if node_dir.exists():
        shutil.rmtree(node_dir)
    extract_to.rename(node_dir)
    zip_path.unlink()

    print(f"Node.js installed at {node_dir}")
    print(f"node: {node_dir / 'node.exe'}")
    print(f"npm: {node_dir / 'npm.cmd'}")
    return node_dir


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    try:
        install(project_root)
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
