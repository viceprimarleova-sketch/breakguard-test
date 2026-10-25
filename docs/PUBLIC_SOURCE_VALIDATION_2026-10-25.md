# Public source validation — October 25, 2026

Runtime checked: `0.1.0rc2`, source
`461558f3d7bc8db06fe89a6137b278163a1ec7c5`. This is a technical evidence update
prepared locally for review, not a new integrated release or customer interview.

## Read-only checks on pinned public sources

All four sources were checked with the installed candidate. Scan and preview
left every tracked source file unchanged; symlink targets were recorded without
following them. No app dependencies were installed, no app code/tests were run,
and no store or live Shopify API was accessed.

| Source | Eligible files scanned / seen | Static documents checked | Documents skipped | Findings |
| --- | --- | --- | --- | --- |
| Official `Shopify/shopify_app` Ruby library | 172 / 286 | 9 | 0 | One manual ScriptTag candidate |
| Official Shopify React Router app template | 19 / 60 | 2 | 0 | None within current rules |
| Public print-integrator application | 43 / 70 | 5 | 0 | One manual ScriptTag candidate |
| Weaverse Pilot Hydrogen storefront | 355 / 562 | 30 | 14 | None within current rules |

Unsupported files are outside the checked rules. Weaverse has an additional
tracked symlink that was skipped, so 563 tracked paths were hashed and 562 files
were seen. Counts are not a measure of general Shopify compatibility or recall.

### Exact source revisions and findings

- Ruby library:
  https://github.com/Shopify/shopify_app/tree/68fd8e4931b2934b6d70950bf398c79310d7268a
  — `lib/shopify_app/managers/script_tags_manager.rb:106`, manual source pattern.
- React Router template:
  https://github.com/Shopify/shopify-app-template-react-router/tree/48b841a7746e1b08d1e6d8793b1208f3096e41d0
  — no supported finding; a control, not a claim that every API is compatible.
- Print-integrator:
  https://github.com/aashishvajatechultra/shopify-print-integrator/tree/5fe4f47497401b4c438ed4ac1f4317538b681cde
  — `app/lib/shopifyProductFetch.server.js:202`, manual ScriptTag source pattern.
  A public report is open at https://github.com/aashishvajatechultra/shopify-print-integrator/issues/1.
  Neither execution of that function nor the maintainer's acceptance is verified.
- Weaverse:
  https://github.com/Weaverse/pilot/tree/ea6d45b362eccb844fec22a25b025ea13087e0b3
  — no supported finding. The only literal keyword found by the independent
  tracked-text search was `ScriptTag` in a Markdown cookbook, not application code.

The first two entries use earlier public revisions; their source dates are not
presented as new platform activity. They were rescanned for this exact runtime.
Full coverage, finding locations and source-preservation records are in
`public-source-validation-2026-10-25.json`. Third-party source is not bundled.

## Weaverse: actual Customer Account documents

The open migration task https://github.com/Weaverse/pilot/issues/191 mentions
Hydrogen 2026.10 and Customer Account removals. Its body does not establish that
the removed field is currently selected in this public application.

A separate offline QA check examined the actual documents under
`app/routes/account`, which `codegen.ts` assigns to the Customer Account schema:

- Seven complete query/mutation documents validated without errors against both
  the named **2026-04** and **2026-10** Customer Account schema snapshots.
- Two additional definitions were fragment-only, not independent operations.
- The orders-list query used same-file template interpolation. The QA check
  composed named local fragments as text; it did not execute JavaScript or imports.
- This QA step is not a product feature. The main CLI still disclosed 14 skipped
  interpolated documents across the application; it does not resolve these strings.

Schema hashes, source commits, operation names and per-document results are in
`weaverse-customer-schema-validation-2026-10-25.json`. The full schema snapshots
come from the official `Shopify/hydrogen` repository paths recorded there.
The application's actual runtime API configuration was not independently
established; these results apply specifically to the two named offline schemas.
No app codegen, response-consumer test, authentication or store execution occurred.

## Product and commercial implication

These are useful negative controls and manual detections, not proof that a
developer needs BreakGuard or will pay. In particular, the Weaverse maintainer
is qualified for expert feedback, not yet as a buyer for the three-rule scope.
See `PILOT_ELIGIBILITY.md` before presenting the complete EUR 49 offer.

Continue with the prepared independent developer protocol. Learn whether the
source report and local workflow change a real next action, and record missing
cases. Improving dynamic-query coverage is a possible future direction; no new
coverage, automatic migration or usefulness claim follows from this QA exercise.
