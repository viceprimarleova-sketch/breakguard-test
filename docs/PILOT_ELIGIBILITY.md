# Pilot eligibility — proposed selection protocol

Status: internal working proposal for selecting the first paid pilot. This is
not a contract, accepted offer or evidence that anyone has agreed to testing.

## Before offering the GBP 42 paid scope

Ask a consenting developer to assess the following locally. No source upload,
store credentials, backup archive or store access is needed. Voluntary, redacted
aggregate answers are sufficient.

1. **Current need:** describe a concrete migration problem and the workflow used
   today. An open issue can describe a plan or a general dependency upgrade;
   confirm whether it actually affects the developer's code now.
2. **Supported case:** identify at least one relevant occurrence from the three
   rule families, actual API surface/version and recognized source form. A field
   name in an issue or documentation does not establish a code occurrence.
3. **Useful result:** independently assess the reported location, guidance and
   limitations. Ask what changes in the developer's next action compared with
   IDE search, Shopify alerts and schema/codegen checks.
4. **Safe local evaluation:** agree a disposable copy, exact source/wheel build,
   preview review, response-consumer checks, the application's own tests and
   restore check. Manual embedded/ScriptTag results remain manual; do not promise
   that all cases receive automatic edits.
5. **Defined commercial scope:** only after fit is established, present the
   complete proposed one-repository offer, limits, support, total/tax, delivery,
   license and refund terms. Verify seller/payment eligibility before charging.
   For the proposed first pilot, the provider-hosted individual invoice and
   delivery are manual (`PAID_PILOT_RUNBOOK.md`). The separate API adapter still
   needs an actual Sandbox transaction before claiming that integration works;
   an offline fake does not validate either route.

## Decision record

| Evidence | Classification | Next step |
| --- | --- | --- |
| Known relevant supported occurrence; developer confirms useful action | Potential paid-pilot fit | Complete the developer protocol and discuss the approved bounded offer |
| No supported occurrence in checked snapshot | Technical control/expert feedback | Ask about usefulness and missing cases; do not count as buyer validation |
| Essential query is dynamic, unrecognized or outside the three families | Coverage gap or different migration need | Record permitted evidence; propose scope changes only when justified |
| Unsafe edit, misleading certainty or failed restore | Technical release blocker | Reproduce and fix before continuing a paid-pilot proposal |
| Positive comment about GBP 42 | Price interest | Record separately from accepting an offer or paying |

## Evidence example, not an interview

`Weaverse/pilot` has an open Hydrogen 2026.10 migration task mentioning the
Customer Account API removal. At pinned revision
`ea6d45b362eccb844fec22a25b025ea13087e0b3`, the current checker found no supported
occurrence. An independent literal search found none in application code.
Fourteen recognized interpolated GraphQL documents were skipped, so this does
not prove complete API compatibility. The maintainer is an expert feedback
candidate; actual need, usefulness and willingness to pay remain unconfirmed.

By contrast, the pinned public print-integrator source has a manual ScriptTag
candidate. That establishes a source pattern, not execution, customer acceptance
or a paid lead. Details are in `PUBLIC_SOURCE_VALIDATION_2026-10-25.md`.
