# BreakGuard V0.1 — 5-minute tester guide

BreakGuard currently targets a small set of known Shopify API deprecations. This build is for controlled external testing, not production-wide automatic migration.

## What it does

- scans a repository for supported Shopify deprecations;
- reports the affected file and line;
- links to the source/remediation recorded in the BreakGuard rule;
- can apply only conservative fixes for rules explicitly marked safe;
- leaves manual-only findings unchanged.

## Requirements

- Python 3.10 or newer;
- Git;
- a local checkout or copy of a Shopify-related code repository.

For the safest test, use a disposable clone or a temporary Git branch.

## Install from the current product branch

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "git+https://github.com/viceprimarleova-sketch/breakguard-test.git@breakguard/product-v0.1"
breakguard --help
```

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install "git+https://github.com/viceprimarleova-sketch/breakguard-test.git@breakguard/product-v0.1"
breakguard --help
```

## Test 1 — scan only

Run against the repository you want to inspect:

```bash
breakguard /path/to/repository
```

BreakGuard prints findings with severity, file, line, remediation, and source.

Important: the current CLI exits with code `1` while findings remain. That is intentional for CI usage and does not mean the scanner crashed.

## Test 2 — JSON output

```bash
breakguard /path/to/repository --json
```

Use this to inspect the machine-readable result.

## Test 3 — conservative automatic fixes

Use only on a disposable clone or a temporary Git branch:

```bash
breakguard /path/to/repository --apply-fixes
```

Then inspect the diff yourself:

```bash
git diff
```

Do not merge or deploy automatically. V0.1 intentionally leaves unsupported/manual migrations untouched.

## What we want from a tester

Please record:

1. operating system and Python version;
2. whether installation completed successfully;
3. repository language/framework;
4. number of findings;
5. any false positive;
6. any deprecation you expected BreakGuard to catch but it missed;
7. whether the remediation text was clear;
8. whether the automatic diff looked safe.

## Current supported rule families

- `Customer.lastIncompleteCheckout` in GraphQL;
- `DraftOrderDiscountNotAppliedWarning.priceRule` in GraphQL;
- legacy `ScriptTag` usage in JavaScript/TypeScript — manual review only.

## Safety boundary

BreakGuard V0.1 is a pre-release developer tool. It should not be treated as a guarantee of compatibility, correctness, or compliance. Always review generated code changes before merge or deployment.
