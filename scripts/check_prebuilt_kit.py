"""Install and verify one prebuilt evaluation archive without rebuilding it."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import zipfile


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    archive_path = args.archive.resolve()
    archive_bytes = archive_path.read_bytes()
    archive_hash = sha256(archive_bytes)
    env = dict(os.environ, PIP_NO_INDEX="1", PIP_DISABLE_PIP_VERSION_CHECK="1")
    env.pop("PYTHONPATH", None)

    with tempfile.TemporaryDirectory(prefix="breakguard prebuilt kit ") as temporary:
        base = Path(temporary)
        unpacked = base / "extracted"
        unpacked.mkdir()
        with zipfile.ZipFile(archive_path) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise ValueError("Archive contains duplicate paths.")
            for name in names:
                path = PurePosixPath(name)
                if path.is_absolute() or ".." in path.parts or not path.parts:
                    raise ValueError(f"Unsafe archive path: {name}")
            archive.extractall(unpacked)

        roots = [p for p in unpacked.iterdir() if p.is_dir()]
        if len(roots) != 1:
            raise ValueError("Expected exactly one top-level kit directory.")
        kit = roots[0]
        sums = (kit / "SHA256SUMS.txt").read_text(encoding="utf-8")
        expected = {}
        for line in sums.splitlines():
            digest, name = line.split("  ", 1)
            if name in expected:
                raise ValueError(f"Duplicate checksum entry: {name}")
            expected[name] = digest
        actual_files = {
            p.relative_to(kit).as_posix()
            for p in kit.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"
        }
        if actual_files != set(expected):
            raise ValueError("Archive file set differs from its checksum manifest.")
        for name, digest in expected.items():
            if sha256((kit / name).read_bytes()) != digest:
                raise ValueError(f"Checksum mismatch: {name}")

        installer = ["cmd", "/c", "install_windows.cmd"] if os.name == "nt" else ["sh", "install_unix.sh"]

        def run(command, *, cwd=kit, expected=0):
            process = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True)
            if process.returncode != expected:
                raise RuntimeError(
                    f"Command failed ({process.returncode}): {command}\\n"
                    f"{process.stdout}\\n{process.stderr}"
                )
            return process

        run(installer)
        python = kit / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        identity = json.loads((kit / "EVALUATION_IDENTITY.json").read_text(encoding="utf-8"))
        hashes = json.loads(run([str(python), "-I", "-c",
            "import breakguard, hashlib, json; from pathlib import Path; "
            "root=Path(breakguard.__file__).resolve().parent.parent; "
            f"names={list(identity['runtime_sha256'])!r}; "
            "print(json.dumps({n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in names}))"
        ]).stdout)
        if hashes != identity["runtime_sha256"]:
            raise ValueError("Installed runtime differs from the archive identity.")

        smoke = json.loads(run([str(python), str(kit / "scripts/release_smoke.py")]).stdout)
        manual = kit / "manual_cases"
        original = {p.name: sha256(p.read_bytes()) for p in manual.iterdir()}
        findings = json.loads(run(
            [str(python), "-m", "breakguard.cli", str(manual), "--apply-fixes", "--json"],
            expected=1,
        ).stdout)
        if len(findings) != 4 or any(f["auto_fix"] is not None for f in findings):
            raise ValueError("Manual-only findings did not remain manual.")
        if original != {p.name: sha256(p.read_bytes()) for p in manual.iterdir()}:
            raise ValueError("Manual-case files were modified.")

        coverage_report = base / "coverage.json"
        run([str(python), "-m", "breakguard.cli", str(kit / "coverage_cases"),
             "--report", str(coverage_report)])
        coverage = json.loads(coverage_report.read_text(encoding="utf-8"))["coverage"]
        if coverage["embedded_documents_skipped"] != 1:
            raise ValueError("Expected dynamic embedded document skip was not reported.")

        print(json.dumps({
            "archive_sha256": archive_hash,
            "source_commit": identity["source_commit"],
            "wheel_sha256": identity["wheel_sha256"],
            "offline_install": "passed",
            "runtime_files_matched": len(hashes),
            "synthetic_workflow": smoke,
            "manual_findings_unchanged": len(findings),
            "dynamic_documents_skipped": coverage["embedded_documents_skipped"],
            "independent_shopify_usefulness_validated": False,
        }, indent=2))


if __name__ == "__main__":
    main()
