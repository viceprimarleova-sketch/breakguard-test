# GraphQL response-name follow-up — October 25, 2026

**State: local review only, based on product commit
`2a56d555931b436551e84b3b8b32803c9c064094`. Not published or integrated.**
The runtime version is still `0.1.0rc2`; this patch is not a new release. The
previous integrated candidate and its hosted checks remain historical evidence
for their exact code, not for this follow-up.

## Reproduced problem

A valid Admin API 2026-07 query can select `discountTitle: message` alongside
`priceRule { title }` on `DraftOrderDiscountNotAppliedWarning`. The original
rc2 edit inserts the field `discountTitle`, which conflicts with the existing
response name. GraphQL syntax parsing succeeds, but full validation against
the official 2026-10 schema rejects the result. The conflict can also occur in
an outer selection or a named fragment.

Five of the eight new regression cases failed before the correction. The
other three ensure that compatible aliases/fragments retain supported edits.

## Correction

Before introducing `discountTitle` or `discountCode`, reserve aliases referring
to different fields across the parsed document. Keep an affected replacement
manual. Also keep replacements manual when a spread refers to a fragment not
defined in that file, because its response names are unknown to this scanner.

This deliberately errs toward manual review: an alias in an unrelated selection
or an external fragment anywhere in the document may suppress an otherwise
safe edit. Known fragments without conflicting aliases remain supported.
Detection continues to report the deprecated field. Preview/apply preserve
manual cases without creating a snapshot or silently removing their finding.

The product CLI still checks syntax rather than loading a Shopify schema.
The new `scripts/validate_schema_migrations.py` is a separate, offline QA tool.

## Completed local validation

- **85 tests passed** against a separately installed wheel on Python 3.12,
  including eight new response-name regressions. All 12 runtime/rule files in
  the wheel and installation matched the reviewed working source.
- **10 synthetic full-schema cases passed**: three supported edits became valid
  on the target schema, and seven manual cases remained visible and unchanged.
  Each original complete query validated against the appropriate older schema.
- Admin schemas: official public introspection endpoint, **2026-07 → 2026-10**.
- Customer Account schemas: Shopify Hydrogen snapshots,
  **2026-04 → 2026-10**. The older version was checked in the repository's
  API constants; it is not claimed to be 2026-07.
- All three automatic cases restored exact original bytes. The installed CLI
  workflow also passed: three findings, two edits, one manual finding, exact
  restore and refusal to overwrite later edits. Payment check was offline only.
- Hosted checks for this follow-up have **not** run. No real Shopify app tests,
  response-consumer tests, store calls or developer acceptance test occurred.

Machine-readable results and exact schema digests are in
`schema-response-review-2026-10-25.json`. Obtain full introspection files locally
from the sources below, then pass them explicitly to the offline QA utility.
It never downloads schemas or sends queries to a store.

## Primary sources

- [Official priceRule migration guidance](https://shopify.dev/changelog/posts/remove-pricerule-from-draft-order-discount-warning)
- [Official Customer Account removal guidance](https://shopify.dev/changelog/posts/customer-account-api-last-incomplete-checkout-and-checkout-types-removed)
- [Official API codegen schema endpoint configuration](https://github.com/Shopify/shopify-app-js/blob/d8a26f4675b4f6e19f2a538712ee5cb47bd584b4/packages/api-clients/api-codegen-preset/src/helpers/api-configs.ts)
- Admin introspection: POST the standard GraphQL introspection query, without
  credentials, to `https://shopify.dev/admin-graphql-direct-proxy/2026-07` and
  `https://shopify.dev/admin-graphql-direct-proxy/2026-10`.
- Customer Account snapshot path:
  `packages/hydrogen/src/graphql/generated/customer-account.schema.json` in
  `Shopify/hydrogen`, commits `a1839530e9a602c86dbda85f6802e53ca80fabc7`
  and `5af8a7d342a974e76234cccf2b38276a2faca9c6`.

## Next gates

1. Founder approves publication of this correction as a review PR. Run hosted
   checks on that exact head, then seek separate final integration approval.
2. Until the correction is integrated, avoid automatic `priceRule` edits in
   documents with the response-name/fragment ambiguity described above.
3. A consenting Shopify developer spends 30–60 minutes on a disposable local
   project: confirm API/version, findings and proposed diff, run their own
   response-consumer/application tests, then test restore. No private source,
   credentials or store access need be shared with BreakGuard.
4. Record usefulness and any willingness to accept the proposed EUR 49 pilot
   separately. Schema validity and demonstrations do not establish either.

No new external messages, public changes, payments or expenses were made in
this follow-up. The separate web prototype remains private. Reddit blocked
the approved introduction in this browser; that message was not sent.
