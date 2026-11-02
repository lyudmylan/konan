# konan scorecard

Generated 2026-11-03T01:32:59+02:00 — 40 scenario(s) scored, model(s): claude-fable-5, claude-sonnet-5.
Deterministic scoring (regex + equality only); semantics: `eval/README.md`.

## Summary

- **Scenarios passed: 29/40**
- Root-cause accuracy: 25/31 (scenarios expecting a root cause)
- False attributions: 4
- Evidence-citation compliance: 40/40
- Tokens: 125465317
- Wall clock: 19807s total

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
| t2-healthy-after-chaos-window | claude-sonnet-5 | ✗ root-cause-identified (want no-active-incident) | — | — | 1 | ✓ | 3161057 | 356 |
| t2-healthy-after-chaos-window | claude-sonnet-5 | ✗ root-cause-identified (want no-active-incident) | — | — | 1 | ✓ | 2585819 | 471 |
| t2-healthy-after-chaos-window | claude-sonnet-5 | ✗ root-cause-identified (want no-active-incident) | — | — | 1 | ✓ | 3660641 | 658 |
| t2-quiet-d1-suggestive-complaint | claude-sonnet-5 | ✓ no-active-incident | — | — | 0 | ✓ | 4468802 | 557 |
| t2-quiet-d1-suggestive-complaint | claude-sonnet-5 | ✗ root-cause-identified (want no-active-incident) | — | — | 1 | ✓ | 2783102 | 464 |
| t2-quiet-d1-suggestive-complaint | claude-sonnet-5 | ✗ inconclusive (want no-active-incident) | — | — | 0 | ✓ | 3556550 | 478 |
| t2-red-herring-latency-latent-d1 | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 3727880 | 793 |
| t2-red-herring-latency-latent-d1 | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 5519175 | 1370 |
| t2-red-herring-latency-latent-d1 | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 3150468 | 719 |
| t3-chaos-low-rate-intermittent | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 2191465 | 360 |
| t3-chaos-low-rate-intermittent | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 5179120 | 901 |
| t3-chaos-low-rate-intermittent | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1905211 | 283 |
| t3-crash-hard-down | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 3105120 | 410 |
| t3-crash-hard-down | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 3902509 | 422 |
| t3-crash-hard-down | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 2140406 | 243 |

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

### t2-healthy-after-chaos-window

- verdict: got `root-cause-identified`, want `no-active-incident`
- cause: got `degradation-switch`, want `None` — false attribution

### t2-healthy-after-chaos-window

- verdict: got `root-cause-identified`, want `no-active-incident`
- cause: got `degradation-switch`, want `None` — false attribution

### t2-healthy-after-chaos-window

- verdict: got `root-cause-identified`, want `no-active-incident`
- cause: got `degradation-switch`, want `None` — false attribution

### t2-quiet-d1-suggestive-complaint

- verdict: got `root-cause-identified`, want `no-active-incident`
- cause: got `unhandled-exception`, want `None` — false attribution

### t2-quiet-d1-suggestive-complaint

- verdict: got `inconclusive`, want `no-active-incident`

### t3-crash-hard-down

- must_claim `no-restart-after`: no match in the claim surface
