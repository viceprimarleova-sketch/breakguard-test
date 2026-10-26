"""Build and install the actual offline kit outside the checkout, then verify it."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

from build_pilot_kit import build_kit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel-dir", required=True, type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    env = dict(os.environ, PIP_NO_INDEX="1", PIP_DISABLE_PIP_VERSION_CHECK="1")
    env.pop("PYTHONPATH", None)
    with tempfile.TemporaryDirectory(prefix="breakguard delivery ") as temporary:
        base = Path(temporary)
        result = build_kit(source, args.wheel_dir, base / "archive")
        unpacked = base / "extracted"
        with zipfile.ZipFile(result["archive"]) as archive:
            archive.extractall(unpacked)
        kit = next(unpacked.iterdir())

        def run(command, *, cwd=base, expected=0):
            process = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True)
            if process.returncode != expected:
                raise RuntimeError(f"Command failed ({process.returncode}): {command}\n"
                                   f"{process.stdout}\n{process.stderr}")
            return process

        installer = ["cmd", "/c", "install_windows.cmd"] if os.name == "nt" else ["sh", "install_unix.sh"]
        run(installer, cwd=kit)
        python = kit / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        identity = json.loads((kit / "EVALUATION_IDENTITY.json").read_text(encoding="utf-8"))
        # Test the installed files, not imports accidentally resolved to checkout.
        hashes = json.loads(run([str(python), "-I", "-c",
            "import breakguard, hashlib, json; from pathlib import Path; "
            "root=Path(breakguard.__file__).resolve().parent.parent; "
            f"names={list(identity['runtime_sha256'])!r}; "
            "print(json.dumps({n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in names}))"
        ]).stdout)
        assert hashes == identity["runtime_sha256"], "Installed package differs from delivery source."
        smoke = json.loads(run([str(python), str(kit / "scripts/release_smoke.py")]).stdout)
        manual = kit / "manual_cases"
        original = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in manual.iterdir()}
        manual_findings = json.loads(run(
            [str(python), "-m", "breakguard.cli", str(manual), "--apply-fixes", "--json"], expected=1,
        ).stdout)
        assert len(manual_findings) == 4 and all(f["auto_fix"] is None for f in manual_findings)
        assert original == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in manual.iterdir()}
        report = base / "coverage.json"
        run([str(python), "-m", "breakguard.cli", str(kit / "coverage_cases"), "--report", str(report)])
        coverage = json.loads(report.read_text(encoding="utf-8"))["coverage"]
        assert coverage["embedded_documents_skipped"] == 1
        print(json.dumps({
            "source_commit": result["source_commit"], "archive_sha256": result["sha256"],
            "wheel_sha256": result["wheel_sha256"], "runtime_files_matched": len(hashes),
            "installer": installer[-1], "offline_install": "passed",
            "synthetic_workflow": smoke, "manual_findings_unchanged": len(manual_findings),
            "dynamic_documents_skipped": coverage["embedded_documents_skipped"],
            "independent_shopify_usefulness_validated": False,
        }, indent=2))


if __name__ == "__main__":
    main()
