"""Read-only raw-byte integrity verification for the locally sealed Java pilot."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys


MANIFEST_DIR = "experiments/java-pilot/manifests"
PILOT = "experiments/original-ai-code/java-inventory-v0"
PROVENANCE = "experiments/java-pilot/provenance"
TESTS = "tests/fixtures/java-inventory-v0"


def checked_path(root, name):
    relative = PurePosixPath(name)
    if relative.is_absolute() or ".." in relative.parts or str(relative) != name:
        raise ValueError(f"Unsafe or noncanonical path: {name}")
    path = root
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError(f"Symlink is not an immutable artifact: {name}")
    return path


def files_under(root, name):
    directory = checked_path(root, name)
    if not directory.is_dir():
        raise ValueError(f"Missing artifact directory: {name}")
    files = set()
    for path in directory.rglob("*"):
        relative = path.relative_to(root).as_posix()
        checked_path(root, relative)
        if path.is_file():
            files.add(relative)
    return files


def verify(root, kind, expected_paths):
    name = f"{MANIFEST_DIR}/{kind}.json"
    path = checked_path(root, name)
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    receipt = checked_path(root, name + ".sha256").read_text(encoding="ascii").strip()
    if receipt != f"{digest}  {kind}.json":
        raise ValueError(f"Manifest hash mismatch: {name}")
    manifest = json.loads(raw)
    if (manifest["format"] != "genesis-raw-byte-manifest"
            or manifest["version"] != 1 or manifest["algorithm"] != "SHA-256"
            or manifest["source_revision"] != "java-inventory-v0.1"):
        raise ValueError(f"Unsupported manifest format/revision: {name}")
    entries = manifest["files"]
    paths = [entry["path"] for entry in entries]
    if paths != sorted(set(paths)) or set(paths) != expected_paths:
        raise ValueError(f"Artifact inventory mismatch: {name}")
    for entry in entries:
        actual = hashlib.sha256(checked_path(root, entry["path"]).read_bytes()).hexdigest()
        if actual != entry["sha256"]:
            raise ValueError(f"Artifact hash mismatch: {entry['path']}")
    print(f"PASS {kind}: {len(entries)} files; manifest SHA-256 {digest}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2],
                        help="repository root; override only for isolated-copy verification")
    args = parser.parse_args()
    root = args.root.resolve()
    source_files = (files_under(root, f"{PILOT}/src/main")
                    | files_under(root, PROVENANCE) | {f"{PILOT}/pom.xml"})
    verify(root, "v0-source", source_files)
    verify(root, "fixed-tests", files_under(root, TESTS))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        sys.exit(f"INTEGRITY FAILED: {error}")
