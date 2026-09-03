# konan scorecard

Generated 2026-08-26T01:54:02+03:00 — 84 scenario(s) scored, model(s): claude-fable-5, claude-opus-5, claude-sonnet-5.
Deterministic scoring (regex + equality only); semantics: `eval/README.md`.

## Summary

- **Scenarios passed: 35/84**
- Root-cause accuracy: 43/59 (scenarios expecting a root cause)
- False attributions: 11
- Evidence-citation compliance: 84/84
- Tokens: 158392605
- Wall clock: 30988s total

## Scenarios

| Scenario | Model | Verdict | Class | Root cause | False attr | Citations | Tokens | Wall (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chaos-error-rate | claude-fable-5 | ✓ root-cause-identified | ✗ | ✗ | 0 | ✓ | 1515260 | 110 |
| chaos-error-rate | claude-fable-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 1398170 | 130 |
| chaos-error-rate | claude-fable-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 1449249 | 138 |
| chaos-latency | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1195824 | 143 |
| chaos-latency | claude-fable-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 1090679 | 150 |
| chaos-latency | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1820235 | 151 |
| d1-zero-stock-product-page | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 2034158 | 187 |
| d1-zero-stock-product-page | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1793799 | 211 |
| d1-zero-stock-product-page | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1892864 | 315 |
| d2-null-price-order | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1422212 | 216 |
| d2-null-price-order | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 2011499 | 323 |
| d2-null-price-order | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 1 | ✓ | 1653953 | 269 |
| healthy-baseline | claude-fable-5 | ✓ no-active-incident | — | — | 0 | ✓ | 2020397 | 450 |
| healthy-baseline | claude-fable-5 | ✓ no-active-incident | — | — | 0 | ✓ | 799239 | 194 |
| healthy-baseline | claude-fable-5 | ✓ no-active-incident | — | — | 0 | ✓ | 1318004 | 184 |
| t2-healthy-after-chaos-window | claude-fable-5 | ✓ no-active-incident | — | — | 0 | ✓ | 1692933 | 412 |
| t2-healthy-after-chaos-window | claude-fable-5 | ✓ no-active-incident | — | — | 0 | ✓ | 1074036 | 251 |
| t2-healthy-after-chaos-window | claude-fable-5 | ✓ no-active-incident | — | — | 0 | ✓ | 1111676 | 228 |
| t2-quiet-d1-suggestive-complaint | claude-fable-5 | ✓ no-active-incident | — | — | 0 | ✓ | 836542 | 284 |
| t2-quiet-d1-suggestive-complaint | claude-fable-5 | ✗ root-cause-identified (want no-active-incident) | — | — | 1 | ✓ | 1311069 | 213 |
| t2-quiet-d1-suggestive-complaint | claude-fable-5 | ✗ root-cause-identified (want no-active-incident) | — | — | 1 | ✓ | 964591 | 216 |
| t2-red-herring-latency-latent-d1 | claude-fable-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 928247 | 275 |
| t2-red-herring-latency-latent-d1 | claude-fable-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 1102605 | 280 |
| t2-red-herring-latency-latent-d1 | claude-fable-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 1277966 | 284 |
| t3-chaos-low-rate-intermittent | claude-fable-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 1862184 | 320 |
| t3-chaos-low-rate-intermittent | claude-fable-5 | ✓ root-cause-identified | ✗ | ✗ | 0 | ✓ | 1227266 | 251 |
| t3-chaos-low-rate-intermittent | claude-fable-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 1259176 | 190 |
| t3-crash-hard-down | claude-fable-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 627860 | 1130 |
| t3-crash-hard-down | claude-fable-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1030788 | 1132 |
| t3-crash-hard-down | claude-fable-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1172049 | 2245 |
| chaos-error-rate | claude-opus-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 2261572 | 528 |
| chaos-error-rate | claude-opus-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 2034527 | 350 |
| chaos-error-rate | claude-opus-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1634705 | 345 |
| chaos-latency | claude-opus-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 2017503 | 327 |
| chaos-latency | claude-opus-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1662950 | 436 |
| chaos-latency | claude-opus-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1265749 | 326 |
| d1-zero-stock-product-page | claude-opus-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1833560 | 327 |
| d1-zero-stock-product-page | claude-opus-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 2119852 | 447 |
| d1-zero-stock-product-page | claude-opus-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1951943 | 254 |
| d2-null-price-order | claude-opus-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 2150278 | 584 |
| d2-null-price-order | claude-opus-5 | ✓ root-cause-identified | ✓ | ✓ | 1 | ✓ | 2534141 | 511 |
| d2-null-price-order | claude-opus-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 2107280 | 555 |
| healthy-baseline | claude-opus-5 | ✓ no-active-incident | — | — | 0 | ✓ | 2556764 | 598 |
| healthy-baseline | claude-opus-5 | ✓ no-active-incident | — | — | 0 | ✓ | 2012134 | 415 |
| healthy-baseline | claude-opus-5 | ✓ no-active-incident | — | — | 0 | ✓ | 2375375 | 369 |
| t2-healthy-after-chaos-window | claude-opus-5 | ✓ no-active-incident | — | — | 0 | ✓ | 1560368 | 518 |
| t2-healthy-after-chaos-window | claude-opus-5 | ✓ no-active-incident | — | — | 0 | ✓ | 774357 | 146 |
| t2-healthy-after-chaos-window | claude-opus-5 | ✓ no-active-incident | — | — | 0 | ✓ | 1067914 | 111 |
| t2-quiet-d1-suggestive-complaint | claude-opus-5 | ✓ no-active-incident | — | — | 0 | ✓ | 1885762 | 364 |
| t2-quiet-d1-suggestive-complaint | claude-opus-5 | ✗ root-cause-identified (want no-active-incident) | — | — | 1 | ✓ | 2476612 | 638 |
| t2-quiet-d1-suggestive-complaint | claude-opus-5 | ✗ root-cause-identified (want no-active-incident) | — | — | 1 | ✓ | 1703228 | 302 |
| t2-red-herring-latency-latent-d1 | claude-opus-5 | ✓ root-cause-identified | ✓ | ✓ | 1 | ✓ | 1690597 | 333 |
| t2-red-herring-latency-latent-d1 | claude-opus-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 1608253 | 337 |
| t2-red-herring-latency-latent-d1 | claude-opus-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 695685 | 120 |
| t3-chaos-low-rate-intermittent | claude-opus-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1342627 | 363 |
| t3-chaos-low-rate-intermittent | claude-opus-5 | ✓ root-cause-identified | ✗ | ✗ | 0 | ✓ | 2463705 | 505 |
| t3-chaos-low-rate-intermittent | claude-opus-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 992663 | 129 |
| t3-crash-hard-down | claude-opus-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 952873 | 314 |
| t3-crash-hard-down | claude-opus-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 546768 | 81 |
| t3-crash-hard-down | claude-opus-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1189116 | 350 |
| chaos-error-rate | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 2218205 | 270 |
| chaos-error-rate | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 6230710 | 701 |
| chaos-error-rate | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 3341568 | 323 |
| chaos-latency | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 2237648 | 344 |
| chaos-latency | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 2797280 | 395 |
| chaos-latency | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 1919764 | 298 |
| d2-null-price-order | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 1 | ✓ | 2233504 | 290 |
| d2-null-price-order | claude-sonnet-5 | ✗ inconclusive (want root-cause-identified) | ✗ | ✗ | 0 | ✓ | 3330594 | 294 |
| d2-null-price-order | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 3269227 | 519 |
| healthy-baseline | claude-sonnet-5 | ✓ no-active-incident | — | — | 0 | ✓ | 2214438 | 468 |
| t2-healthy-after-chaos-window | claude-sonnet-5 | ✗ root-cause-identified (want no-active-incident) | — | — | 1 | ✓ | 3487235 | 317 |
| t2-healthy-after-chaos-window | claude-sonnet-5 | ✗ root-cause-identified (want no-active-incident) | — | — | 1 | ✓ | 3263802 | 391 |
| t2-healthy-after-chaos-window | claude-sonnet-5 | ✓ no-active-incident | — | — | 0 | ✓ | 2026426 | 299 |
| t2-quiet-d1-suggestive-complaint | claude-sonnet-5 | ✓ no-active-incident | — | — | 0 | ✓ | 2813219 | 323 |
| t2-quiet-d1-suggestive-complaint | claude-sonnet-5 | ✗ inconclusive (want no-active-incident) | — | — | 0 | ✓ | 2205670 | 433 |
| t2-quiet-d1-suggestive-complaint | claude-sonnet-5 | ✗ root-cause-identified (want no-active-incident) | — | — | 1 | ✓ | 1943301 | 212 |
| t2-red-herring-latency-latent-d1 | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 2745307 | 513 |
| t2-red-herring-latency-latent-d1 | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 4027052 | 781 |
| t2-red-herring-latency-latent-d1 | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 1660984 | 322 |
| t3-chaos-low-rate-intermittent | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 3499438 | 309 |
| t3-chaos-low-rate-intermittent | claude-sonnet-5 | ✓ root-cause-identified | ✗ | ✓ | 0 | ✓ | 2097977 | 269 |
| t3-crash-hard-down | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 2140394 | 293 |
| t3-crash-hard-down | claude-sonnet-5 | ✗ inconclusive (want root-cause-identified) | ✗ | ✗ | 0 | ✓ | 2037711 | 379 |
| t3-crash-hard-down | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 2287760 | 380 |

## Failure detail

### chaos-error-rate

- incident class: got `interfaces`
- must_claim `spread`: no match in the claim surface

### chaos-error-rate

- incident class: got `interfaces`

### chaos-error-rate

- incident class: got `interfaces`

### chaos-latency

- incident class: got `interfaces`

### d2-null-price-order

- must_not_claim `not-infra`: FIRED — false attribution

### t2-quiet-d1-suggestive-complaint

- verdict: got `root-cause-identified`, want `no-active-incident`
- must_not_claim `no-promoted-latent-defect`: FIRED — false attribution

### t2-quiet-d1-suggestive-complaint

- verdict: got `root-cause-identified`, want `no-active-incident`
- must_not_claim `no-promoted-latent-defect`: FIRED — false attribution

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
- must_claim `rare-but-real`: no match in the claim surface

### t3-chaos-low-rate-intermittent

- incident class: got `interfaces`

### t3-crash-hard-down

- must_claim `no-restart-after`: no match in the claim surface

### t3-crash-hard-down

- must_claim `no-restart-after`: no match in the claim surface

### t3-crash-hard-down

- must_claim `no-restart-after`: no match in the claim surface

### chaos-error-rate

- incident class: got `interfaces`

### chaos-error-rate

- must_claim `spread`: no match in the claim surface

### chaos-error-rate

- must_claim `spread`: no match in the claim surface

### d1-zero-stock-product-page

- must_claim `location`: no match in the claim surface

### d2-null-price-order

- must_not_claim `not-d1-misattribution`: FIRED — false attribution

### t2-quiet-d1-suggestive-complaint

- verdict: got `root-cause-identified`, want `no-active-incident`
- must_not_claim `no-promoted-latent-defect`: FIRED — false attribution

### t2-quiet-d1-suggestive-complaint

- verdict: got `root-cause-identified`, want `no-active-incident`
- must_not_claim `no-promoted-latent-defect`: FIRED — false attribution

### t2-red-herring-latency-latent-d1

- must_not_claim `latent-defect-not-promoted`: FIRED — false attribution

### t2-red-herring-latency-latent-d1

- incident class: got `interfaces`

### t3-chaos-low-rate-intermittent

- must_claim `rare-but-real`: no match in the claim surface

### t3-chaos-low-rate-intermittent

- incident class: got `interfaces`
- must_claim `rare-but-real`: no match in the claim surface

### t3-chaos-low-rate-intermittent

- incident class: got `interfaces`

### t3-crash-hard-down

- must_claim `no-restart-after`: no match in the claim surface

### t3-crash-hard-down

- must_claim `no-restart-after`: no match in the claim surface

### chaos-error-rate

- incident class: got `interfaces`

### chaos-error-rate

- incident class: got `interfaces`

### chaos-error-rate

- incident class: got `interfaces`

### chaos-latency

- incident class: got `interfaces`

### chaos-latency

- incident class: got `interfaces`

### d2-null-price-order

- must_not_claim `not-infra`: FIRED — false attribution

### d2-null-price-order

- verdict: got `inconclusive`, want `root-cause-identified`
- incident class: got `None`
- must_claim `mechanism`: no match in the claim surface
- must_claim `operation`: no match in the claim surface
- must_claim `data-condition`: no match in the claim surface

### t2-healthy-after-chaos-window

- verdict: got `root-cause-identified`, want `no-active-incident`
- must_not_claim `past-window-not-active`: FIRED — false attribution

### t2-healthy-after-chaos-window

- verdict: got `root-cause-identified`, want `no-active-incident`
- must_not_claim `past-window-not-active`: FIRED — false attribution

### t2-quiet-d1-suggestive-complaint

- verdict: got `inconclusive`, want `no-active-incident`

### t2-quiet-d1-suggestive-complaint

- verdict: got `root-cause-identified`, want `no-active-incident`
- must_not_claim `no-promoted-latent-defect`: FIRED — false attribution

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

### t3-crash-hard-down

- must_claim `no-restart-after`: no match in the claim surface

### t3-crash-hard-down

- verdict: got `inconclusive`, want `root-cause-identified`
- incident class: got `None`
- must_claim `process-died`: no match in the claim surface
- must_claim `no-restart-after`: no match in the claim surface

### t3-crash-hard-down

- must_claim `no-restart-after`: no match in the claim surface
