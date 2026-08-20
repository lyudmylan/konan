# konan benchmark — results

Runs: bench-v1. 77 investigations. Protocol and limits: `eval/BENCHMARK.md`.
Deterministic scoring (eval/score.py); tokens = whole run incl. subagents; duration = harness wall clock.
Pass rate is the pre-registered metric; the class-agnostic column ignores only the incident-class label (taxonomy issue tracked separately).

## Per tier × model

| Tier | Model | Runs | Failed | Pass rate | Pass (class-agnostic) | Root-cause acc. | False attr. | Citations | Tokens (median) | Wall s (median) | Cost $ (median) | Denials (median) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | claude-fable-5 | 15 | 0 | 67% | 87% | 92% | 1 | 100% | 1515260 | 236 | 4.30 | 7.0 |
| 1 | claude-opus-5 | 15 | 0 | 67% | 73% | 75% | 1 | 100% | 2034527 | 530 | 3.46 | 9.0 |
| 1 | claude-sonnet-5 | 15 | 5 | 20% | 53% | 89% | 1 | 67% | 2218205 | 211 | 1.99 | 4.0 |
| 2 | claude-fable-5 | 2 | 1 | 50% | 50% | — | 0 | 50% | 1692933 | 118 | 2.75 | 1.5 |
| 2 | claude-opus-5 | 9 | 0 | 56% | 67% | 100% | 3 | 100% | 1608253 | 492 | 3.08 | 9.0 |
| 2 | claude-sonnet-5 | 9 | 0 | 22% | 56% | 100% | 3 | 100% | 2745307 | 418 | 2.15 | 5.0 |
| 3 | claude-opus-5 | 6 | 0 | 17% | 33% | 33% | 0 | 100% | 1090890 | 329 | 2.35 | 4.0 |
| 3 | claude-sonnet-5 | 6 | 1 | 0% | 33% | 40% | 0 | 83% | 2119186 | 276 | 1.75 | 3.0 |
| all | claude-fable-5 | 17 | 1 | 65% | 82% | 92% | 1 | 94% | 1584606 | 235 | 4.30 | 5.0 |
| all | claude-opus-5 | 30 | 0 | 53% | 63% | 67% | 4 | 100% | 1768394 | 496 | 3.28 | 7.0 |
| all | claude-sonnet-5 | 30 | 6 | 17% | 50% | 76% | 4 | 80% | 2216322 | 364 | 1.95 | 4.0 |

## Quota: investigations completed between quota stops (per model)

A proxy for investigations per 5-hour window on the subscription; exact only when a batch starts near an empty window with nothing else on the pool. Segments = runs before each stop; the last number is the open segment.

- claude-fable-5: [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] + open 0
- claude-opus-5: [3, 0, 0, 0, 0, 11, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0] + open 5
- claude-sonnet-5: [6, 0, 0, 0, 0] + open 24

## Every run

| Run | Model | Scenario | Tier | Rep | Status | Verdict | Expected | Passed | RC | False attr | Citations | Tokens | Wall s | Cost $ | Denials |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bench-v1 | claude-fable-5 | chaos-error-rate | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 1515260 | 227 | 3.38 | 9 |
| bench-v1 | claude-fable-5 | chaos-error-rate | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 0 | ✓ | 1398170 | 224 | 3.05 | 7 |
| bench-v1 | claude-fable-5 | chaos-error-rate | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 0 | ✓ | 1449249 | 232 | 4.30 | 7 |
| bench-v1 | claude-opus-5 | chaos-error-rate | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 0 | ✓ | 2261572 | 714 | 4.11 | 13 |
| bench-v1 | claude-opus-5 | chaos-error-rate | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 2034527 | 530 | 3.43 | 10 |
| bench-v1 | claude-opus-5 | chaos-error-rate | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 1634705 | 235 | 3.00 | 2 |
| bench-v1 | claude-sonnet-5 | chaos-error-rate | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 0 | ✓ | 2218205 | 150 | 2.04 | 3 |
| bench-v1 | claude-sonnet-5 | chaos-error-rate | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 0 | ✓ | 6230710 | 175 | 4.06 | 1 |
| bench-v1 | claude-sonnet-5 | chaos-error-rate | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 0 | ✓ | 3341568 | 540 | 2.63 | 9 |
| bench-v1 | claude-fable-5 | chaos-latency | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1195824 | 236 | 4.20 | 4 |
| bench-v1 | claude-fable-5 | chaos-latency | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 0 | ✓ | 1090679 | 261 | 4.09 | 9 |
| bench-v1 | claude-fable-5 | chaos-latency | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1820235 | 141 | 4.09 | 5 |
| bench-v1 | claude-opus-5 | chaos-latency | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 2017503 | 590 | 3.42 | 7 |
| bench-v1 | claude-opus-5 | chaos-latency | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1662950 | 603 | 3.16 | 9 |
| bench-v1 | claude-opus-5 | chaos-latency | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1265749 | 480 | 2.64 | 5 |
| bench-v1 | claude-sonnet-5 | chaos-latency | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 0 | ✓ | 2237648 | 466 | 1.90 | 13 |
| bench-v1 | claude-sonnet-5 | chaos-latency | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 2797280 | 559 | 2.44 | 9 |
| bench-v1 | claude-sonnet-5 | chaos-latency | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 0 | ✓ | 1919764 | 211 | 1.66 | 0 |
| bench-v1 | claude-fable-5 | d1-zero-stock-product-page | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 2034158 | 103 | 4.70 | 5 |
| bench-v1 | claude-fable-5 | d1-zero-stock-product-page | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1793799 | 354 | 7.02 | 7 |
| bench-v1 | claude-fable-5 | d1-zero-stock-product-page | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1892864 | 165 | 5.59 | 3 |
| bench-v1 | claude-opus-5 | d1-zero-stock-product-page | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1833560 | 487 | 3.31 | 11 |
| bench-v1 | claude-opus-5 | d1-zero-stock-product-page | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 2119852 | 515 | 3.57 | 10 |
| bench-v1 | claude-opus-5 | d1-zero-stock-product-page | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 1951943 | 194 | 3.25 | 2 |
| bench-v1 | claude-sonnet-5 | d1-zero-stock-product-page | 1 | 1 | no-journal | — | root-cause-identified | ✗ | — | 0 | ✗ | 374804 | 27 | 0.25 | 3 |
| bench-v1 | claude-sonnet-5 | d1-zero-stock-product-page | 1 | 2 | no-journal | — | root-cause-identified | ✗ | — | 0 | ✗ | 333186 | 22 | 0.20 | 3 |
| bench-v1 | claude-sonnet-5 | d1-zero-stock-product-page | 1 | 3 | no-journal | — | root-cause-identified | ✗ | — | 0 | ✗ | 432096 | 31 | 0.20 | 4 |
| bench-v1 | claude-fable-5 | d2-null-price-order | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1422212 | 184 | 4.78 | 1 |
| bench-v1 | claude-fable-5 | d2-null-price-order | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 2011499 | 310 | 5.37 | 3 |
| bench-v1 | claude-fable-5 | d2-null-price-order | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 1 | ✓ | 1653953 | 480 | 5.35 | 10 |
| bench-v1 | claude-opus-5 | d2-null-price-order | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 2150278 | 719 | 3.89 | 10 |
| bench-v1 | claude-opus-5 | d2-null-price-order | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 1 | ✓ | 2534141 | 344 | 4.64 | 0 |
| bench-v1 | claude-opus-5 | d2-null-price-order | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 2107280 | 724 | 4.03 | 15 |
| bench-v1 | claude-sonnet-5 | d2-null-price-order | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 1 | ✓ | 2233504 | 417 | 1.99 | 8 |
| bench-v1 | claude-sonnet-5 | d2-null-price-order | 1 | 2 | ok | inconclusive | root-cause-identified | ✗ | ✗ | 0 | ✓ | 3330594 | 254 | 2.50 | 3 |
| bench-v1 | claude-sonnet-5 | d2-null-price-order | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 3269227 | 739 | 2.98 | 12 |
| bench-v1 | claude-fable-5 | healthy-baseline | 1 | 1 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 2020397 | 639 | 6.00 | 12 |
| bench-v1 | claude-fable-5 | healthy-baseline | 1 | 2 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 799239 | 287 | 2.82 | 4 |
| bench-v1 | claude-fable-5 | healthy-baseline | 1 | 3 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 1318004 | 378 | 3.73 | 10 |
| bench-v1 | claude-opus-5 | healthy-baseline | 1 | 1 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 2556764 | 821 | 4.41 | 8 |
| bench-v1 | claude-opus-5 | healthy-baseline | 1 | 2 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 2012134 | 612 | 3.46 | 10 |
| bench-v1 | claude-opus-5 | healthy-baseline | 1 | 3 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 2375375 | 176 | 3.89 | 0 |
| bench-v1 | claude-sonnet-5 | healthy-baseline | 1 | 1 | no-journal | — | no-active-incident | ✗ | — | 0 | ✗ | 422903 | 32 | 0.24 | 4 |
| bench-v1 | claude-sonnet-5 | healthy-baseline | 1 | 2 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 2214438 | 543 | 2.26 | 10 |
| bench-v1 | claude-sonnet-5 | healthy-baseline | 1 | 3 | no-journal | — | no-active-incident | ✗ | — | 0 | ✗ | 344992 | 25 | 0.17 | 3 |
| bench-v1 | claude-fable-5 | t2-healthy-after-chaos-window | 2 | 1 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 1692933 | 235 | 5.51 | 3 |
| bench-v1 | claude-fable-5 | t2-healthy-after-chaos-window | 2 | 2 | error | — | no-active-incident | ✗ | — | 0 | ✗ | — | 1 | 0.00 | 0 |
| bench-v1 | claude-opus-5 | t2-healthy-after-chaos-window | 2 | 1 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 1560368 | 664 | 3.48 | 7 |
| bench-v1 | claude-opus-5 | t2-healthy-after-chaos-window | 2 | 2 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 774357 | 269 | 1.37 | 1 |
| bench-v1 | claude-opus-5 | t2-healthy-after-chaos-window | 2 | 3 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 1067914 | 248 | 1.34 | 2 |
| bench-v1 | claude-sonnet-5 | t2-healthy-after-chaos-window | 2 | 1 | ok | root-cause-identified | no-active-incident | ✗ | — | 1 | ✓ | 3487235 | 370 | 2.50 | 4 |
| bench-v1 | claude-sonnet-5 | t2-healthy-after-chaos-window | 2 | 2 | ok | root-cause-identified | no-active-incident | ✗ | — | 1 | ✓ | 3263802 | 185 | 2.41 | 4 |
| bench-v1 | claude-sonnet-5 | t2-healthy-after-chaos-window | 2 | 3 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 2026426 | 418 | 1.80 | 5 |
| bench-v1 | claude-opus-5 | t2-quiet-d1-suggestive-complaint | 2 | 1 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 1885762 | 542 | 3.35 | 9 |
| bench-v1 | claude-opus-5 | t2-quiet-d1-suggestive-complaint | 2 | 2 | ok | root-cause-identified | no-active-incident | ✗ | — | 1 | ✓ | 2476612 | 871 | 5.16 | 9 |
| bench-v1 | claude-opus-5 | t2-quiet-d1-suggestive-complaint | 2 | 3 | ok | root-cause-identified | no-active-incident | ✗ | — | 1 | ✓ | 1703228 | 454 | 3.08 | 12 |
| bench-v1 | claude-sonnet-5 | t2-quiet-d1-suggestive-complaint | 2 | 1 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 2813219 | 478 | 2.15 | 11 |
| bench-v1 | claude-sonnet-5 | t2-quiet-d1-suggestive-complaint | 2 | 2 | ok | inconclusive | no-active-incident | ✗ | — | 0 | ✓ | 2205670 | 528 | 2.12 | 7 |
| bench-v1 | claude-sonnet-5 | t2-quiet-d1-suggestive-complaint | 2 | 3 | ok | root-cause-identified | no-active-incident | ✗ | — | 1 | ✓ | 1943301 | 442 | 1.57 | 9 |
| bench-v1 | claude-opus-5 | t2-red-herring-latency-latent-d1 | 2 | 1 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 1 | ✓ | 1690597 | 499 | 3.08 | 9 |
| bench-v1 | claude-opus-5 | t2-red-herring-latency-latent-d1 | 2 | 2 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 0 | ✓ | 1608253 | 492 | 3.06 | 10 |
| bench-v1 | claude-opus-5 | t2-red-herring-latency-latent-d1 | 2 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 695685 | 247 | 1.16 | 1 |
| bench-v1 | claude-sonnet-5 | t2-red-herring-latency-latent-d1 | 2 | 1 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 0 | ✓ | 2745307 | 173 | 2.51 | 1 |
| bench-v1 | claude-sonnet-5 | t2-red-herring-latency-latent-d1 | 2 | 2 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 0 | ✓ | 4027052 | 689 | 3.43 | 5 |
| bench-v1 | claude-sonnet-5 | t2-red-herring-latency-latent-d1 | 2 | 3 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 0 | ✓ | 1660984 | 407 | 1.68 | 6 |
| bench-v1 | claude-opus-5 | t3-chaos-low-rate-intermittent | 3 | 1 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 1342627 | 550 | 3.01 | 7 |
| bench-v1 | claude-opus-5 | t3-chaos-low-rate-intermittent | 3 | 2 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 2463705 | 252 | 4.08 | 1 |
| bench-v1 | claude-opus-5 | t3-chaos-low-rate-intermittent | 3 | 3 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 0 | ✓ | 992663 | 271 | 1.45 | 1 |
| bench-v1 | claude-sonnet-5 | t3-chaos-low-rate-intermittent | 3 | 1 | no-journal | — | root-cause-identified | ✗ | — | 0 | ✗ | 360848 | 71 | 0.31 | 2 |
| bench-v1 | claude-sonnet-5 | t3-chaos-low-rate-intermittent | 3 | 2 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 0 | ✓ | 3499438 | 359 | 2.62 | 1 |
| bench-v1 | claude-sonnet-5 | t3-chaos-low-rate-intermittent | 3 | 3 | ok | root-cause-identified | root-cause-identified | ✗ | ✓ | 0 | ✓ | 2097977 | 104 | 1.75 | 1 |
| bench-v1 | claude-opus-5 | t3-crash-hard-down | 3 | 1 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 952873 | 388 | 2.18 | 7 |
| bench-v1 | claude-opus-5 | t3-crash-hard-down | 3 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 546768 | 183 | 0.91 | 3 |
| bench-v1 | claude-opus-5 | t3-crash-hard-down | 3 | 3 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 1189116 | 513 | 2.52 | 5 |
| bench-v1 | claude-sonnet-5 | t3-crash-hard-down | 3 | 1 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 2140394 | 443 | 1.83 | 12 |
| bench-v1 | claude-sonnet-5 | t3-crash-hard-down | 3 | 2 | ok | inconclusive | root-cause-identified | ✗ | ✗ | 0 | ✓ | 2037711 | 194 | 1.61 | 4 |
| bench-v1 | claude-sonnet-5 | t3-crash-hard-down | 3 | 3 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 2287760 | 501 | 1.75 | 10 |
