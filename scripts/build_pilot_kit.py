"""Build a free technical evaluation from a clean, pinned source; never upload.

The former private review pack mixed technical delivery with commercial drafts
and a historical wheel hash. Only the explicit technical allowlist is shipped.
"""
import argparse
import ast
import configparser
from email.parser import BytesParser
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile


TEMPLATES = (
    "README_EN.md", "START_HERE_RO.md", "install_windows.cmd",
    "install_unix.sh", "verify_kit.py", "PUBLIC_SOURCE_NOTES.md",
)
TECHNICAL_FILES = {
    "TESTER_GUIDE.md": "TESTER_GUIDE.md",
    "docs/FEEDBACK_TEMPLATE.md": "FEEDBACK_TEMPLATE.md",
    "scripts/release_smoke.py": "scripts/release_smoke.py",
}
EXAMPLES = {
    "demo_project/customer.graphql": "query Buyer { customer { id lastIncompleteCheckout { id } } }\n",
    "demo_project/warning.graphql": "fragment Discount on DraftOrderDiscountNotAppliedWarning { priceRule { title } }\n",
    "demo_project/legacy.js": "// Synthetic query; never sent to a store.\nconst m = `mutation Demo($input: ScriptTagInput!) { scriptTagCreate(input: $input) { scriptTag { id } } }`;\n",
    "manual_cases/customer_only.graphql": "query Buyer { customer { lastIncompleteCheckout { id } } }\n",
    "manual_cases/customer.ts": "const q = `#graphql\nquery Buyer { customer { id lastIncompleteCheckout { id } } }`;\n",
    "manual_cases/discount.rb": "QUERY = <<~QUERY\nfragment Discount on DraftOrderDiscountNotAppliedWarning { priceRule { title } }\nQUERY\n",
    "manual_cases/warning_alias.graphql": "fragment Discount on DraftOrderDiscountNotAppliedWarning { discountTitle: __typename priceRule { title } }\n",
    "coverage_cases/dynamic.ts": "const q = `#graphql\nquery Buyer { customer { ${selection} } }`;\n",
    "coverage_cases/notes.txt": "Unsupported file type; outside the source rules.\n",
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def git(repo, *arguments):
    return subprocess.run(
        ["git", *arguments], cwd=repo, check=True, capture_output=True,
    ).stdout


def committed(repo, name):
    return git(repo, "show", f"HEAD:{name}")


def source_version(data):
    for node in ast.parse(data.decode("utf-8")).body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "__version__"
            for target in node.targets
        ):
            version = ast.literal_eval(node.value)
            if isinstance(version, str) and version and all(
                c.isalnum() or c in ".+-" for c in version
            ):
                return version
    raise ValueError("Cannot determine the committed package version.")


def verify_wheel(data, runtime, version):
    """Reject old same-version code/rules and unexpected installed payloads."""
    import io

    metadata_root = f"breakguard-{version}.dist-info/"
    metadata_names = {
        metadata_root + name for name in
        ("METADATA", "WHEEL", "entry_points.txt", "top_level.txt", "RECORD")
    }
    with zipfile.ZipFile(io.BytesIO(data)) as wheel:
        names = wheel.namelist()
        if len(names) != len(set(names)) or set(names) != set(runtime) | metadata_names:
            raise ValueError("Wheel payload differs from the committed package file list.")
        for name, expected in runtime.items():
            if wheel.read(name) != expected:
                raise ValueError(f"Wheel source mismatch: {name}")
        metadata = BytesParser().parsebytes(wheel.read(metadata_root + "METADATA"))
        if metadata["Name"] != "breakguard" or metadata["Version"] != version:
            raise ValueError("Wheel package name/version mismatch.")
        entry_points = configparser.ConfigParser()
        entry_points.read_string(wheel.read(metadata_root + "entry_points.txt").decode())
        if (entry_points.sections() != ["console_scripts"] or
                dict(entry_points["console_scripts"]) != {"breakguard": "breakguard.cli:main"}):
            raise ValueError("Unexpected wheel entry points.")
        layout = BytesParser().parsebytes(wheel.read(metadata_root + "WHEEL"))
        if layout["Root-Is-Purelib"] != "true" or layout.get_all("Tag") != ["py3-none-any"]:
            raise ValueError("Expected a pure Python, platform-independent wheel.")


def build_kit(repo, wheel_dir, out_dir):
    repo, wheel_dir, out_dir = Path(repo).resolve(), Path(wheel_dir).resolve(), Path(out_dir).resolve()
    if git(repo, "status", "--porcelain", "--untracked-files=normal").strip():
        raise ValueError("Commit the reviewed local changes before building the kit.")
    candidate = git(repo, "rev-parse", "HEAD").decode().strip()
    tracked = git(repo, "ls-files", "-z", "--", "breakguard").decode().split("\0")
    runtime = {name: committed(repo, name) for name in tracked if name}
    version = source_version(runtime["breakguard/__init__.py"])
    wheel_name = f"breakguard-{version}-py3-none-any.whl"
    wheel = (wheel_dir / wheel_name).read_bytes()
    verify_wheel(wheel, runtime, version)

    dependency = json.loads(committed(repo, "evaluation/DEPENDENCY_LOCK.json"))
    dependency_name = dependency["filename"]
    if Path(dependency_name).name != dependency_name or not dependency_name.endswith(".whl"):
        raise ValueError("Invalid dependency wheel name.")
    dependency_wheel = (wheel_dir / dependency_name).read_bytes()
    if sha256(dependency_wheel) != dependency["sha256"]:
        raise ValueError("Dependency wheel checksum mismatch.")
    with zipfile.ZipFile(wheel_dir / dependency_name) as archive:
        dependency_license = archive.read(dependency["license_member"])

    files = {
        name: committed(repo, "evaluation/" + name).replace(b"{{VERSION}}", version.encode("ascii"))
        for name in TEMPLATES
    }
    files.update({destination: committed(repo, source) for source, destination in TECHNICAL_FILES.items()})
    files.update({name: content.encode("utf-8") for name, content in EXAMPLES.items()})
    files.update({
        "wheels/" + wheel_name: wheel,
        "wheels/" + dependency_name: dependency_wheel,
        "GRAPHQL_CORE_LICENSE.txt": dependency_license,
        "DEPENDENCY_LOCK.json": json_bytes(dependency),
        "EVALUATION_IDENTITY.json": json_bytes({
            "kit_format": 1, "version": version, "source_commit": candidate,
            "runtime_sha256": {name: sha256(data) for name, data in runtime.items()},
            "wheel_filename": wheel_name, "wheel_sha256": sha256(wheel),
            "dependency": dependency, "payment_required": False,
            "evaluation": "voluntary technical feedback; not commercial acceptance",
        }),
    })
    files["SHA256SUMS.txt"] = "".join(
        f"{sha256(data)}  {name}\n" for name, data in sorted(files.items())
    ).encode("utf-8")

    stem = f"BreakGuard_Developer_Evaluation_{version}_{candidate[:12]}"
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / (stem + ".zip")
    # Exclusive creation preserves already delivered archives; fixed metadata
    # makes repeated builds from the same bytes reproducible on all platforms.
    created = False
    try:
        with zipfile.ZipFile(output, "x", zipfile.ZIP_STORED) as archive:
            created = True
            for name, data in sorted(files.items()):
                info = zipfile.ZipInfo(stem + "/" + name, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = (0o100755 if name == "install_unix.sh" else 0o100644) << 16
                # Wheels are already compressed. Stored entries also avoid
                # platform-specific zlib output for identical input bytes.
                info.compress_type = zipfile.ZIP_STORED
                archive.writestr(info, data)
        with zipfile.ZipFile(output) as archive:
            if archive.testzip() is not None:
                raise ValueError("Archive integrity check failed.")
    except BaseException:
        if created:
            output.unlink(missing_ok=True)
        raise
    return {
        "archive": str(output), "bytes": output.stat().st_size,
        "sha256": sha256(output.read_bytes()), "source_commit": candidate,
        "wheel_sha256": sha256(wheel), "manifest_files": len(files) - 1,
        "runtime_files_verified": len(runtime), "payment_required": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = build_kit(Path(__file__).resolve().parents[1], args.wheel_dir, args.out_dir)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, subprocess.CalledProcessError) as error:
        parser.exit(2, f"Cannot build evaluation kit: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
