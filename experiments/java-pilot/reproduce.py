"""Build the controlled synthetic pilot in a disposable copy of its sealed inputs."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

from verify_integrity import MANIFEST_DIR, PILOT, checked_path


def run(command, cwd):
    print("COMMAND " + json.dumps(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True, timeout=300)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--maven", default="mvn", help="Maven 3.9.11 executable")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    verifier = root / "experiments/java-pilot/verify_integrity.py"
    run([sys.executable, str(verifier)], root)
    version = subprocess.check_output([args.maven, "-version"], text=True, timeout=30)
    print(version, flush=True)
    if "Apache Maven 3.9.11 " not in version or "Java version: 21." not in version:
        raise ValueError("Reproduction requires Maven 3.9.11 running on Java 21")
    with tempfile.TemporaryDirectory(prefix="genesis-java-v0-") as directory:
        copy_root = Path(directory)
        for kind in ("v0-source", "fixed-tests"):
            manifest_path = f"{MANIFEST_DIR}/{kind}.json"
            manifest = json.loads((root / manifest_path).read_bytes())
            names = [entry["path"] for entry in manifest["files"]]
            for name in names + [manifest_path, manifest_path + ".sha256"]:
                source = checked_path(root, name)
                destination = checked_path(copy_root, name)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
        run([sys.executable, str(verifier), "--root", str(copy_root)], root)
        try:
            run([args.maven, "-B", "-ntp", "-f", f"{PILOT}/pom.xml", "clean", "verify"],
                copy_root)
        finally:
            run([sys.executable, str(verifier), "--root", str(copy_root)], root)
            run([sys.executable, str(verifier)], root)
        report = ET.parse(copy_root / PILOT / "target/surefire-reports/TEST-org.genesis.pilot.InventoryTest.xml").getroot()
        summary = {name: int(report.attrib[name]) for name in ("tests", "failures", "errors", "skipped")}
        summary["test_cases"] = [case.attrib["name"] for case in report.findall("testcase")]
        if summary["tests"] != 10 or any(summary[name] for name in ("failures", "errors", "skipped")):
            raise ValueError(f"Unexpected fixed-suite result: {summary}")
        jar = copy_root / PILOT / "target/java-inventory-v0-0.1.0.jar"
        summary["jar_sha256"] = hashlib.sha256(jar.read_bytes()).hexdigest()
        summary["execution_scope"] = "temporary derivative; original files verified before and after"
        print("SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        sys.exit(f"REPRODUCTION FAILED: {error}")
