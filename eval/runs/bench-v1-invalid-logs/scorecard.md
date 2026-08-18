# konan scorecard

Generated 2026-08-19T01:14:50+03:00 — 23 scenario(s) scored, model(s): claude-sonnet-5.
Deterministic scoring (regex + equality only); semantics: `eval/README.md`.

## Summary

- **Scenarios passed: 9/23**
- Root-cause accuracy: 13/16 (scenarios expecting a root cause)
- False attributions: 3
- Evidence-citation compliance: 23/23
- Tokens: 80143046
- Wall clock: 9455s total

## Scenarios

| Scenario | Model | Verdict | Class | Root cause | False attr | Citations | Tokens | Wall (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chaos-error-rate | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 3094328 | 299 |
| chaos-error-rate | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✗ | 0 | ✓ | 2167451 | 230 |
| chaos-latency | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 2810613 | 475 |
| chaos-latency | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 2997684 | 465 |
| chaos-latency | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 2441519 | 278 |
| d1-zero-stock-product-page | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 3431908 | 311 |
| d1-zero-stock-product-page | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 3832755 | 323 |
| d2-null-price-order | claude-sonnet-5 | ✗ inconclusive (want root-cause-identified) | ✗ | ✗ | 0 | ✓ | 3078503 | 438 |
| d2-null-price-order | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 1 | ✓ | 3943750 | 553 |
| healthy-baseline | claude-sonnet-5 | ✓ no-active-incident | — | — | 0 | ✓ | 1585078 | 110 |
| healthy-baseline | claude-sonnet-5 | ✓ no-active-incident | — | — | 0 | ✓ | 2788863 | 203 |
| healthy-baseline | claude-sonnet-5 | ✓ no-active-incident | — | — | 0 | ✓ | 2676519 | 238 |
| t2-healthy-after-chaos-window | claude-sonnet-5 | ✓ no-active-incident | — | — | 0 | ✓ | 5641951 | 634 |
| t2-healthy-after-chaos-window | claude-sonnet-5 | ✓ no-active-incident | — | — | 0 | ✓ | 4977979 | 624 |
| t2-quiet-d1-suggestive-complaint | claude-sonnet-5 | ✗ inconclusive (want no-active-incident) | — | — | 0 | ✓ | 3911480 | 491 |
| t2-quiet-d1-suggestive-complaint | claude-sonnet-5 | ✓ no-active-incident | — | — | 0 | ✓ | 3662081 | 289 |
| t2-red-herring-latency-latent-d1 | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 3887163 | 532 |
| t2-red-herring-latency-latent-d1 | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 3899024 | 431 |
| t2-red-herring-latency-latent-d1 | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 2710850 | 442 |
| t3-chaos-low-rate-intermittent | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 4921562 | 481 |
| t3-chaos-low-rate-intermittent | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✓ | 1 | ✓ | 5982738 | 885 |
| t3-crash-hard-down | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1113966 | 222 |
| t3-crash-hard-down | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 1 | ✓ | 4585281 | 501 |

## Failure detail

### chaos-error-rate

- incident class: got `interfaces`
- must_claim `spread`: no match in the claim surface

### chaos-latency

- incident class: got `interfaces`

### chaos-latency

- incident class: got `interfaces`

### chaos-latency

- incident class: got `interfaces`

### d2-null-price-order

- verdict: got `inconclusive`, want `root-cause-identified`
- incident class: got `None`
- must_claim `mechanism`: no match in the claim surface
- must_claim `data-condition`: no match in the claim surface

### d2-null-price-order

- must_not_claim `not-chaos`: FIRED — false attribution

### t2-quiet-d1-suggestive-complaint

- verdict: got `inconclusive`, want `no-active-incident`

### t2-red-herring-latency-latent-d1

- incident class: got `interfaces`

### t2-red-herring-latency-latent-d1

- incident class: got `interfaces`

### t2-red-herring-latency-latent-d1

- incident class: got `interfaces`

### t3-chaos-low-rate-intermittent

- incident class: got `interfaces`

### t3-chaos-low-rate-intermittent

- incident class: got `interfaces`
- must_not_claim `not-code-defect`: FIRED — false attribution

### t3-crash-hard-down

- must_claim `no-restart-after`: no match in the claim surface

### t3-crash-hard-down

- must_not_claim `not-code-defect`: FIRED — false attribution
