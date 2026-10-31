# Reproducible free evaluation delivery

The kit is a technical evaluation, not a paid offer or final release. The
builder and verifier are integrated in PR #10 at
`b65f1125abb43f05cca659f7e645dff397901518`. External distribution of a new
candidate remains subject to the Founder's approval.

## Build from the source being reviewed

Use a clean checkout and Python 3.10+. Keep wheel/output directories outside the
checkout. These preparation commands can download build tools and the pinned
dependency; the delivered installer itself does not download packages:

```sh
python -m pip wheel --no-deps --wheel-dir ../evaluation-wheels .
python -m pip download --only-binary=:all: --no-deps --dest ../evaluation-wheels graphql-core==3.2.13
python scripts/build_pilot_kit.py --wheel-dir ../evaluation-wheels --out-dir ../evaluation-output
python scripts/check_delivery_kit.py --wheel-dir ../evaluation-wheels
```

The existing script name is retained, but its output is now a free technical
evaluation. It no longer creates the old private commercial review bundle.
Use the repository's separate working commercial documents for internal review.

## What is checked

- Every installed runtime/rule file in the wheel must match the exact committed
  `breakguard/` tree. Old same-version wheels and unexpected installed payloads
  are refused. Package identity, entry points and pure-Python layout are checked.
- The included GraphQL dependency is pinned by version **and SHA-256** in
  `evaluation/DEPENDENCY_LOCK.json`; its MIT license is included. Updating the
  dependency requires reviewing and updating that lock, not trusting a new file
  merely because its name is unchanged.
- An explicit allowlist includes EN/RO technical instructions, installers,
  a verifier, smoke protocol, empty feedback template, dated public-source
  evidence and synthetic examples. Seller intake, invoices, contact records,
  commercial terms, payment instructions, patches and arbitrary repository
  files are not included.
- `EVALUATION_IDENTITY.json` records the full source commit, wheel/dependency
  hashes and all runtime hashes. `SHA256SUMS.txt` covers all delivered files
  except itself. SHA-256 is integrity evidence, not a signed publisher identity.
- The ZIP name includes the source prefix. Existing archives are never replaced.
  Sorting, fixed metadata and stored ZIP entries produce identical archives from
  identical source and wheel bytes, independent of compression-library output.
- Installers verify the archive contents before creating/reusing `.venv` and
  force reinstall from the included wheels. The verifier excludes `.venv`, which
  is generated locally and is not part of delivered-file integrity evidence.

## Test the actual artifact

`scripts/check_delivery_kit.py` builds and extracts a new ZIP into a temporary
path containing spaces, then runs the actual Windows or Unix installer. It runs
outside the checkout, removes `PYTHONPATH`, disables pip package downloads and
compares all installed runtime hashes with the kit identity. It then checks:

1. Synthetic detection → preview → two edits → rescan → exact restore.
2. Refusal to overwrite a developer's later edit.
3. Four manual cases remain unchanged; one dynamic document is disclosed as skipped.
4. Payment simulation remains an offline fake, with no transaction or fulfillment.

The external-install GitHub job includes this protocol on Ubuntu/macOS/Windows.
Adding the job steps is not evidence that they have already run. Record each
actual local/hosted result against its precise commit. A failed packaging or
install check blocks distribution of that artifact.

## Delivery identity and independent usefulness

Never silently change a previously shared ZIP or Drive file when a new build is
prepared. Keep the already delivered build and its historical evidence intact.
A new candidate requires its own reviewed identity and delivery decision.
The external-install workflow for the integrated source passed on Ubuntu,
macOS and Windows. The workflow artifact listing returned no downloadable ZIP
during this review. Build a fresh archive from the exact integrated commit,
record its hashes, extract it and inspect/install it before calling it the final
deliverable. A prepared ZIP is not a published release.
