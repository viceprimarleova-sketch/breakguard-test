"""Check delivered file integrity before installation; no network or source upload."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys


def verify(root):
    root = Path(root).resolve()
    expected = {}
    for line in (root / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        digest, separator, name = line.partition("  ")
        relative = PurePosixPath(name)
        if (not separator or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest)
                or not name or "\\" in name or relative.is_absolute()
                or any(part in (".", "..") for part in name.split("/"))
                or name in expected or name == "SHA256SUMS.txt"):
            raise ValueError("Invalid checksum manifest.")
        expected[name] = digest
    if not expected:
        raise ValueError("Empty checksum manifest.")
    installed = root / ".venv"
    if installed.is_symlink():
        raise ValueError("The local environment must not be a symbolic link.")
    actual = set()
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if relative.parts[0] == ".venv":
            continue  # Installed environment is not part of the delivered archive.
        if path.is_symlink():
            raise ValueError(f"Unexpected symbolic link: {relative.as_posix()}")
        if path.is_file():
            actual.add(relative.as_posix())
    if actual != set(expected) | {"SHA256SUMS.txt"}:
        raise ValueError("Missing or additional delivery files; extract into a new folder.")
    for name, digest in expected.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Checksum mismatch: {name}")
    return {"status": "verified", "delivered_files_checked": len(expected)}


def main():
    try:
        result = verify(Path(__file__).resolve().parent)
    except (OSError, ValueError) as error:
        print(f"Delivery verification failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
