# BreakGuard rc2 — developer validation, 30–60 minutes

Status: prepared test protocol; no Shopify developer has yet completed this
protocol. A passing demonstration is functional evidence, not customer validation.

## 1. Safe setup — 5 minutes

Install the exact wheel from the kit using its README. Record `breakguard
--version`, OS, Python version and the public repository commit (or a private
local identifier that will not be shared). Work in a disposable clone or a clean
temporary Git branch. No credentials, private code or store access are requested.

The synthetic `demo_project` should have three findings: two standalone GraphQL
edits and one manual ScriptTag result. After preview and apply there should be one
manual finding. `manual_cases` adds static embedded examples that must never be
changed and a customer-only selection that must stay manual. `coverage_cases`
contains an interpolated query that should be counted as skipped.

## 2. Representative code — 10–15 minutes

Choose a repository/framework the developer actually understands. Identify its
Shopify API surface and configured version locally. If it contains no supported
legacy usage, record that as a control; do not label an injected example as a real
application discovery. Where possible choose a public historical revision with
a known supported case, with permission to use its license.

Run `breakguard REPO --report before.json` with the report outside REPO. Record
coverage counts, findings and unsupported/dynamic documents. An exit code of `1`
is normal while findings remain; `2` is an error and stops the test.

Independently search for the three supported families using the developer's IDE
or `rg`. Classify each reported location as relevant, irrelevant or uncertain;
record known missed locations and why they were missed. Do not infer recall or
precision across Shopify from one repository.

## 3. Review, edit and restore — 10–20 minutes

Run `breakguard REPO --fix-preview`. Confirm the source is unchanged. For every
proposed edit, confirm API scope, target version, surrounding selection and code
that consumes the response. Decline edits the developer cannot assess.

On the disposable copy only, run `breakguard REPO --apply-fixes --report
after.json`. Compare the applied diff with the preview, then run that
application's own tests using its documented command. BreakGuard's CLI does not
run those tests or certify a live Shopify schema. Keep ScriptTag and embedded
findings manual.

Run `breakguard REPO --restore PRINTED_BACKUP_ID` and confirm original bytes
return. Separately verify, on a disposable example, that editing a changed file
after apply makes restore refuse the operation rather than overwrite later work.
Keep the local backup if needed; never upload it to us.

## 4. Independent usefulness — 10–15 minutes

Ask the developer to describe their last migration and how they found affected
code. Show the report, then ask:

1. Which finding or explanation changes what you would do next?
2. What is missing or misleading? Which source forms are essential?
3. How does this compare with your current search, schema validation and Shopify
   dashboard workflow?
4. Would you use the current workflow again on a real migration? What would
   have to improve first? Record a concrete example in the developer's own words.

This free technical evaluation does not require a price discussion, purchase
commitment or payment. If the developer later requests an assisted paid pilot,
qualify the supported case and review the separately approved offer and terms.

Record answers in `FEEDBACK_TEMPLATE.md`. Share only voluntary, redacted findings
and aggregate counts; source files, backups, store identifiers and secrets stay
local. Do not start a charge during a validation session.

## Candidate acceptance record

- Installation and CLI path: pass/fail + environment.
- Known supported locations: reported/missed/uncertain, with permitted evidence.
- Proposed/applied diff and application test outcome: pass/fail/not tested.
- Restore/conflict behavior: pass/fail.
- Developer's usefulness judgment: verbatim permissioned short feedback.
- Any later commercial follow-up: record separately; do not count free testing
  as accepting an offer or paying.

An unsafe edit or operational false success blocks release. Unsupported essential
source forms change the product scope before a commercial promise is made.
