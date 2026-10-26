# Public source observations — checks performed October 25, 2026

Historical technical evidence, not a new application test. These four sources
were scanned read-only using BreakGuard 0.1.0rc2 at source commit
`461558f3d7bc8db06fe89a6137b278163a1ec7c5`. The kit's own exact build identity is
recorded separately in `EVALUATION_IDENTITY.json`.

| Pinned source | Eligible files scanned / seen | Static documents checked | Dynamic documents skipped | Findings |
| --- | --- | --- | --- | --- |
| Shopify Ruby library | 172 / 286 | 9 | 0 | One manual ScriptTag source pattern |
| Shopify React Router template | 19 / 60 | 2 | 0 | No supported finding |
| Public print-integrator app | 43 / 70 | 5 | 0 | One manual ScriptTag source pattern |
| Weaverse Pilot storefront | 355 / 562 | 30 | 14 | No supported finding |

Exact revisions and relevant locations:

- [Shopify/shopify_app](https://github.com/Shopify/shopify_app/tree/68fd8e4931b2934b6d70950bf398c79310d7268a):
  `lib/shopify_app/managers/script_tags_manager.rb`, line 106.
- [Shopify React Router template](https://github.com/Shopify/shopify-app-template-react-router/tree/48b841a7746e1b08d1e6d8793b1208f3096e41d0):
  negative control within the three-rule scope.
- [Public print-integrator](https://github.com/aashishvajatechultra/shopify-print-integrator/tree/5fe4f47497401b4c438ed4ac1f4317538b681cde):
  `app/lib/shopifyProductFetch.server.js`, line 202, manual `scriptTagCreate` pattern.
- [Weaverse/pilot](https://github.com/Weaverse/pilot/tree/ea6d45b362eccb844fec22a25b025ea13087e0b3):
  negative control with 14 recognized dynamic documents skipped. One tracked
  symlink was also skipped; 562 files were seen across 563 tracked paths.

Tracked sources remained unchanged. No application dependencies were installed,
no application code or tests were executed, and no store or live Shopify API
was accessed. Third-party source is not included in this kit. Source dates are
not presented as new activity. A source pattern does not prove execution or a
developer's current problem; a zero result does not certify API compatibility.

These observations support a concrete independent test: choose a repository
you understand, confirm its actual API/version, compare reported and independently
known locations, review response consumers, and run the application's own tests.
The supplied synthetic examples demonstrate the workflow; neither those examples
nor the public scans establish independent developer usefulness or safety on a
real Shopify application.
