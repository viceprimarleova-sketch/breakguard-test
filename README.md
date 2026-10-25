# BreakGuard V0.1

**0.1.0rc2 — integrated for controlled testing; commercial validation remains open.**

BreakGuard is a local Python tool for three known Shopify deprecation rule
families. It reports file/line locations and official guidance, previews
supported edits, saves local originals before applying, and can restore them
when subsequent edits do not conflict. It does not connect to a Shopify store.

## Install the reviewed candidate

The delivery kit contains a wheel and its pinned dependency. From the extracted
kit, create a virtual environment and install without downloading packages:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --force-reinstall --no-index --find-links wheels breakguard==0.1.0rc2
.\.venv\Scripts\breakguard.exe --version
```

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --force-reinstall --no-index --find-links wheels breakguard==0.1.0rc2
.venv/bin/breakguard --version
```

Python 3.10 or newer is required. Runtime source at commit
`461558f3d7bc8db06fe89a6137b278163a1ec7c5` passed 85 installed-package tests
and hosted checks on Python 3.10–3.12, plus the installed workflow on Ubuntu,
macOS and Windows. PR #7 integrated the response-name guard with the Founder's
approval. These results apply to that exact source, not a final commercial release.

Use `--force-reinstall` when replacing an earlier rc2 build: its version number
alone does not distinguish the earlier wheel from the corrected one. Check the
source commit and wheel hash in the delivery kit.

The product branch now provides rc2 directly (Git is required for this route):

```sh
python -m pip install --force-reinstall "git+https://github.com/viceprimarleova-sketch/breakguard-test.git@breakguard/product-v0.1"
breakguard --version
```

For reproducible evaluations, pin the tested commit recorded in the delivery
kit. For example, the integrated runtime verified above can be installed with:

```sh
python -m pip install --force-reinstall "git+https://github.com/viceprimarleova-sketch/breakguard-test.git@461558f3d7bc8db06fe89a6137b278163a1ec7c5"
```

For a local source checkout, use `python -m pip install '.[test]'` instead.

## Detect → preview → edit → verify → restore

Work on a disposable clone or a temporary Git branch first:

```sh
breakguard /path/to/repository --report before.json
breakguard /path/to/repository --fix-preview
breakguard /path/to/repository --apply-fixes --report after.json
breakguard /path/to/repository --json
# Review the diff and run that application's own tests locally.
# Use the actual identifier printed during apply:
breakguard /path/to/repository --restore BACKUP_ID
```

Reports must use a new `.json` destination; existing files are never overwritten.
They contain coverage, rule fingerprints, limitations and findings, not source
snippets. A report may expose file names; redact before sharing it.

Exit codes: `0` means no supported findings remain, `1` means findings remain,
and `2` means an operational/internal error. An empty result does not establish
Shopify API compatibility. `--json` remains a JSON array; progress goes to stderr.
Use `--report` rather than `--json` together with `--fix-preview`.

## Coverage

| Rule family | Standalone `.graphql` / `.gql` | Recognized embedded queries |
| --- | --- | --- |
| Customer Account `Customer.lastIncompleteCheckout` | Detection and guarded proposed removal | Manual finding only |
| Admin `DraftOrderDiscountNotAppliedWarning.priceRule` | Detection and guarded proposed replacement | Manual finding only |
| ScriptTag creation/update | Manual source-pattern review | Manual source-pattern review |

Embedded field detection recognizes static JS/TS template literals marked
`#graphql`, tagged `gql`/`graphql`, or passed directly to a `graphql`/`gql` call,
and Ruby `GRAPHQL`/`GQL`/`QUERY`/`MUTATION` heredocs. This is a limited heuristic, not a full host
language parser. Interpolation, malformed documents, other string forms,
languages and generated code can be missed. Coverage counts disclose recognized
documents that were skipped. Scripts are never executed by the scanner.

Aliases, removed variables/fragments, empty selections, invalid syntax and
unsupported price-rule data stay manual. ScriptTag tests/fixtures and read/delete
patterns are excluded. All findings need the developer to confirm the actual API
surface and version. Edits check GraphQL syntax, not a Shopify schema, runtime
behavior or application response consumers. Application tests are not run by the
main CLI; the optional GitHub helper runs an operator-selected verification command.

## Local edit safety and data

Scan and preview do not change source. Apply snapshots only the files it changes
under `.breakguard/backups/BACKUP_ID/`, with hashes and a snapshot-level ignore
file to keep originals out of ordinary Git adds even when the project already
has its own `.breakguard/.gitignore`. Existing project settings are preserved.
Backups created by the earlier build are not changed by this correction; check
their Git-ignore status locally before staging files. Backups contain source and stay on the
developer's machine. Restore validates all files first and refuses later edits
or corrupted snapshots. Do not edit concurrently or manually change manifests.
Snapshots supplement the developer's Git workflow; they are not remote backups.

Symlinks/out-of-root targets are excluded or rejected; unsupported/non-UTF8 files
and ignored directories are counted or excluded. Permission/read errors fail the
scan instead of producing a successful empty result. The local scanner has no
network calls, account requirement or telemetry. The separate opt-in GitHub helper
can push a review branch and create a Draft PR using an operator-provided token;
it never automatically merges and never resets an existing local review branch.

## Pilot preparation

See `docs/PILOT_READINESS.md`, `docs/PILOT_ELIGIBILITY.md`, `TESTER_GUIDE.md`, `docs/PILOT_OFFER_DRAFT.md`,
`docs/PILOT_TERMS_DRAFT.md` and `docs/PAYMENT_TESTING.md`.

The operator-only payment module supports an offline simulation and a PayPal
Sandbox adapter. There is no live mode or automatic fulfillment:

```sh
python -m breakguard.pilot_payments --simulate
```

The private synthetic web prototype remains a separate demonstration. It is not
a Shopify integration or a live checkout. This work does not publish it.
