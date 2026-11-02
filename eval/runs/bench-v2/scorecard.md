# konan scorecard

Generated 2026-11-02T23:38:20+02:00 — 30 scenario(s) scored, model(s): claude-fable-5, claude-sonnet-5.
Deterministic scoring (regex + equality only); semantics: `eval/README.md`.

## Summary

- **Scenarios passed: 23/30**
- Root-cause accuracy: 19/24 (scenarios expecting a root cause)
- False attributions: 1
- Evidence-citation compliance: 30/30
- Tokens: 94483501
- Wall clock: 14984s total

## Scenarios

| Scenario | Model | Verdict | Class | Root cause | False attr | Citations | Tokens | Wall (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chaos-error-rate | claude-fable-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 2573526 | 484 |
| chaos-error-rate | claude-fable-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1977653 | 378 |
| chaos-error-rate | claude-fable-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1712411 | 311 |
| chaos-latency | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 947226 | 368 |
| d1-zero-stock-product-page | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1567282 | 396 |
| d1-zero-stock-product-page | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 2217577 | 496 |
| d1-zero-stock-product-page | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 2035336 | 431 |
| d2-null-price-order | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1741232 | 481 |
| d2-null-price-order | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1387191 | 423 |
| d2-null-price-order | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1283988 | 406 |
| chaos-error-rate | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 3450833 | 421 |
| chaos-error-rate | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 5902420 | 488 |
| chaos-error-rate | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 3381155 | 518 |
| chaos-latency | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 5501939 | 552 |
| chaos-latency | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 3376881 | 536 |
| chaos-latency | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 6485960 | 764 |
| d1-zero-stock-product-page | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 3191717 | 434 |
| d1-zero-stock-product-page | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1788749 | 314 |
| d1-zero-stock-product-page | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 3222963 | 571 |
| d2-null-price-order | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 4706238 | 817 |
| d2-null-price-order | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 2758669 | 522 |
| d2-null-price-order | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 2544903 | 390 |
| healthy-baseline | claude-sonnet-5 | ✓ no-active-incident | — | — | 0 | ✓ | 3733117 | 241 |
| healthy-baseline | claude-sonnet-5 | ✓ no-active-incident | — | — | 0 | ✓ | 2547705 | 340 |
| healthy-baseline | claude-sonnet-5 | ✓ no-active-incident | — | — | 0 | ✓ | 4391321 | 240 |
| t2-quiet-d1-suggestive-complaint | claude-sonnet-5 | ✓ no-active-incident | — | — | 0 | ✓ | 4468802 | 557 |
| t2-quiet-d1-suggestive-complaint | claude-sonnet-5 | ✗ root-cause-identified (want no-active-incident) | — | — | 1 | ✓ | 2783102 | 464 |
| t2-quiet-d1-suggestive-complaint | claude-sonnet-5 | ✗ inconclusive (want no-active-incident) | — | — | 0 | ✓ | 3556550 | 478 |
| t2-red-herring-latency-latent-d1 | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 3727880 | 793 |
| t2-red-herring-latency-latent-d1 | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 5519175 | 1370 |

## Failure detail

### chaos-error-rate

- must_claim `spread`: no match in the claim surface

### chaos-error-rate

- must_claim `spread`: no match in the claim surface

### chaos-error-rate

- must_claim `spread`: no match in the claim surface

### chaos-error-rate

- must_claim `spread`: no match in the claim surface

### d1-zero-stock-product-page

- must_claim `data-condition`: no match in the claim surface

### t2-quiet-d1-suggestive-complaint

- verdict: got `root-cause-identified`, want `no-active-incident`
- cause: got `unhandled-exception`, want `None` — false attribution

### t2-quiet-d1-suggestive-complaint

- verdict: got `inconclusive`, want `no-active-incident`
