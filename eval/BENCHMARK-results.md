# konan benchmark — results

Coverage: complete, 90 of 90 planned runs.

Runs: bench-v2. 90 investigations. Protocol and limits: `eval/BENCHMARK.md`.
Deterministic scoring (eval/score.py); tokens = whole run incl. subagents; duration = harness wall clock.
Pass rate is the pre-registered metric; the class-agnostic column ignores only the incident-class label (taxonomy issue tracked separately).
Medians cover completed investigations (status ok); failed runs count in Runs/Failed and their consumption stays in the sidecars.

## Coverage

Planned = the pre-registered plan of the run (`plan.json`: fixtures × repetitions); a quota stop is not a run.

- bench-v2 claude-fable-5: planned 30, completed 30, failed 0, missing 0
- bench-v2 claude-opus-5: planned 30, completed 29, failed 1, missing 0
- bench-v2 claude-sonnet-5: planned 30, completed 30, failed 0, missing 0

## Per tier × model

| Tier | Model | Runs | Failed | Pass rate | Pass (class-agnostic) | Root-cause acc. | False attr. | Citations | Tokens (median) | Wall s (median) | Cost $ (median) | Denials (median) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | claude-fable-5 | 15 | 0 | 80% | 80% | 75% | 0 | 100% | 1567282 | 434 | 6.76 | 0.0 |
| 1 | claude-opus-5 | 15 | 0 | 73% | 73% | 67% | 0 | 100% | 2302244 | 610 | 4.61 | 0.0 |
| 1 | claude-sonnet-5 | 15 | 0 | 87% | 87% | 83% | 0 | 100% | 3381155 | 558 | 1.99 | 3.0 |
| 2 | claude-fable-5 | 9 | 0 | 56% | 56% | 100% | 4 | 100% | 1587432 | 388 | 6.73 | 0.0 |
| 2 | claude-opus-5 | 9 | 1 | 56% | 56% | 100% | 2 | 89% | 2228723 | 726 | 4.69 | 0.5 |
| 2 | claude-sonnet-5 | 9 | 0 | 44% | 44% | 100% | 4 | 100% | 3556550 | 757 | 2.07 | 3.0 |
| 3 | claude-fable-5 | 6 | 0 | 100% | 100% | 100% | 0 | 100% | 855381 | 394 | 3.89 | 0.0 |
| 3 | claude-opus-5 | 6 | 0 | 50% | 50% | 50% | 0 | 100% | 1734480 | 509 | 3.74 | 0.5 |
| 3 | claude-sonnet-5 | 6 | 0 | 83% | 83% | 83% | 0 | 100% | 2648292 | 425 | 1.71 | 2.5 |
| all | claude-fable-5 | 30 | 0 | 77% | 77% | 86% | 4 | 100% | 1466432 | 405 | 6.12 | 0.0 |
| all | claude-opus-5 | 30 | 1 | 63% | 63% | 67% | 2 | 97% | 2205017 | 610 | 4.57 | 0.0 |
| all | claude-sonnet-5 | 30 | 0 | 73% | 73% | 86% | 4 | 100% | 3379018 | 576 | 2.00 | 3.0 |

## Quota: investigations completed between quota stops (per model)

A proxy for investigations per 5-hour window on the subscription; exact only when a batch starts near an empty window with nothing else on the pool. Segments = runs before each stop; the last number is the open segment.

- claude-fable-5: — + open 30
- claude-opus-5: — + open 30
- claude-sonnet-5: — + open 30

## Every run

| Run | Model | Scenario | Tier | Rep | Status | Verdict | Expected | Passed | RC | False attr | Citations | Tokens | Wall s | Cost $ | Denials |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bench-v2 | claude-fable-5 | chaos-error-rate | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 2573526 | 747 | 7.45 | 3 |
| bench-v2 | claude-fable-5 | chaos-error-rate | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 1977653 | 434 | 5.86 | 1 |
| bench-v2 | claude-fable-5 | chaos-error-rate | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 1712411 | 388 | 5.23 | 2 |
| bench-v2 | claude-opus-5 | chaos-error-rate | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 2302244 | 226 | 4.79 | 0 |
| bench-v2 | claude-opus-5 | chaos-error-rate | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 2446858 | 881 | 5.27 | 0 |
| bench-v2 | claude-opus-5 | chaos-error-rate | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 2362790 | 298 | 4.57 | 0 |
| bench-v2 | claude-sonnet-5 | chaos-error-rate | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 3450833 | 601 | 1.88 | 4 |
| bench-v2 | claude-sonnet-5 | chaos-error-rate | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 5902420 | 823 | 2.56 | 9 |
| bench-v2 | claude-sonnet-5 | chaos-error-rate | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 3381155 | 195 | 2.07 | 0 |
| bench-v2 | claude-fable-5 | chaos-latency | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 947226 | 505 | 5.29 | 0 |
| bench-v2 | claude-fable-5 | chaos-latency | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1462132 | 608 | 6.96 | 1 |
| bench-v2 | claude-fable-5 | chaos-latency | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1335364 | 207 | 4.58 | 0 |
| bench-v2 | claude-opus-5 | chaos-latency | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1975228 | 769 | 4.16 | 0 |
| bench-v2 | claude-opus-5 | chaos-latency | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1701870 | 706 | 3.94 | 0 |
| bench-v2 | claude-opus-5 | chaos-latency | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1794838 | 777 | 4.27 | 0 |
| bench-v2 | claude-sonnet-5 | chaos-latency | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 5501939 | 411 | 2.80 | 0 |
| bench-v2 | claude-sonnet-5 | chaos-latency | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 3376881 | 757 | 1.99 | 3 |
| bench-v2 | claude-sonnet-5 | chaos-latency | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 6485960 | 284 | 3.12 | 1 |
| bench-v2 | claude-fable-5 | d1-zero-stock-product-page | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1567282 | 599 | 7.50 | 4 |
| bench-v2 | claude-fable-5 | d1-zero-stock-product-page | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 2217577 | 186 | 8.22 | 2 |
| bench-v2 | claude-fable-5 | d1-zero-stock-product-page | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 2035336 | 10 | 7.30 | 0 |
| bench-v2 | claude-opus-5 | d1-zero-stock-product-page | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 2560299 | 259 | 4.91 | 0 |
| bench-v2 | claude-opus-5 | d1-zero-stock-product-page | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 1993854 | 610 | 3.98 | 3 |
| bench-v2 | claude-opus-5 | d1-zero-stock-product-page | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 2104505 | 278 | 4.61 | 0 |
| bench-v2 | claude-sonnet-5 | d1-zero-stock-product-page | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 3191717 | 594 | 1.91 | 2 |
| bench-v2 | claude-sonnet-5 | d1-zero-stock-product-page | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1788749 | 418 | 1.18 | 1 |
| bench-v2 | claude-sonnet-5 | d1-zero-stock-product-page | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 3222963 | 797 | 2.03 | 3 |
| bench-v2 | claude-fable-5 | d2-null-price-order | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1741232 | 673 | 6.93 | 3 |
| bench-v2 | claude-fable-5 | d2-null-price-order | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1387191 | 296 | 6.63 | 0 |
| bench-v2 | claude-fable-5 | d2-null-price-order | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1283988 | 583 | 6.76 | 0 |
| bench-v2 | claude-opus-5 | d2-null-price-order | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1767130 | 469 | 4.27 | 0 |
| bench-v2 | claude-opus-5 | d2-null-price-order | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1927339 | 928 | 4.74 | 3 |
| bench-v2 | claude-opus-5 | d2-null-price-order | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 2342381 | 506 | 4.60 | 0 |
| bench-v2 | claude-sonnet-5 | d2-null-price-order | 1 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 4706238 | 1071 | 2.84 | 10 |
| bench-v2 | claude-sonnet-5 | d2-null-price-order | 1 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 2758669 | 724 | 1.95 | 3 |
| bench-v2 | claude-sonnet-5 | d2-null-price-order | 1 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 2544903 | 558 | 1.61 | 3 |
| bench-v2 | claude-fable-5 | healthy-baseline | 1 | 1 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 1348458 | 296 | 6.11 | 0 |
| bench-v2 | claude-fable-5 | healthy-baseline | 1 | 2 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 1975081 | 146 | 7.59 | 0 |
| bench-v2 | claude-fable-5 | healthy-baseline | 1 | 3 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 980634 | 592 | 4.83 | 0 |
| bench-v2 | claude-opus-5 | healthy-baseline | 1 | 1 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 2442318 | 901 | 4.71 | 2 |
| bench-v2 | claude-opus-5 | healthy-baseline | 1 | 2 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 3594610 | 1333 | 6.82 | 1 |
| bench-v2 | claude-opus-5 | healthy-baseline | 1 | 3 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 3016297 | 275 | 4.94 | 0 |
| bench-v2 | claude-sonnet-5 | healthy-baseline | 1 | 1 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 3733117 | 412 | 2.01 | 0 |
| bench-v2 | claude-sonnet-5 | healthy-baseline | 1 | 2 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 2547705 | 411 | 1.29 | 3 |
| bench-v2 | claude-sonnet-5 | healthy-baseline | 1 | 3 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 4391321 | 264 | 1.79 | 0 |
| bench-v2 | claude-fable-5 | t2-healthy-after-chaos-window | 2 | 1 | ok | root-cause-identified | no-active-incident | ✗ | — | 1 | ✓ | 1470732 | 388 | 5.34 | 0 |
| bench-v2 | claude-fable-5 | t2-healthy-after-chaos-window | 2 | 2 | ok | root-cause-identified | no-active-incident | ✗ | — | 1 | ✓ | 1205295 | 513 | 5.14 | 0 |
| bench-v2 | claude-fable-5 | t2-healthy-after-chaos-window | 2 | 3 | ok | root-cause-identified | no-active-incident | ✗ | — | 1 | ✓ | 1876049 | 429 | 7.30 | 0 |
| bench-v2 | claude-opus-5 | t2-healthy-after-chaos-window | 2 | 1 | unscorable: journal eval/runs/bench-v2/claude-opus-5/t2-healthy-after-chaos-window-r1.md: frontmatter is not YAML (while parsing a block mapping
  in "<unicode string>", line 138, column 5:
      - id: E15
        ^
expected <block end>, but found '<block mapping start>'
  in "<unicode string>", line 144, column 7:
          ZeroDivisionError: division by zero
          ^) | — | no-active-incident | ✗ | — | 0 | ✗ | 2551187 | 1046 | 5.62 | 0 |
| bench-v2 | claude-opus-5 | t2-healthy-after-chaos-window | 2 | 2 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 2288064 | 813 | 4.56 | 0 |
| bench-v2 | claude-opus-5 | t2-healthy-after-chaos-window | 2 | 3 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 2225723 | 796 | 4.70 | 1 |
| bench-v2 | claude-sonnet-5 | t2-healthy-after-chaos-window | 2 | 1 | ok | root-cause-identified | no-active-incident | ✗ | — | 1 | ✓ | 3161057 | 176 | 1.82 | 0 |
| bench-v2 | claude-sonnet-5 | t2-healthy-after-chaos-window | 2 | 2 | ok | root-cause-identified | no-active-incident | ✗ | — | 1 | ✓ | 2585819 | 757 | 1.86 | 4 |
| bench-v2 | claude-sonnet-5 | t2-healthy-after-chaos-window | 2 | 3 | ok | root-cause-identified | no-active-incident | ✗ | — | 1 | ✓ | 3660641 | 196 | 2.15 | 0 |
| bench-v2 | claude-fable-5 | t2-quiet-d1-suggestive-complaint | 2 | 1 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 1334351 | 317 | 5.49 | 0 |
| bench-v2 | claude-fable-5 | t2-quiet-d1-suggestive-complaint | 2 | 2 | ok | root-cause-identified | no-active-incident | ✗ | — | 1 | ✓ | 2120531 | 199 | 8.00 | 0 |
| bench-v2 | claude-fable-5 | t2-quiet-d1-suggestive-complaint | 2 | 3 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 1556970 | 795 | 7.33 | 1 |
| bench-v2 | claude-opus-5 | t2-quiet-d1-suggestive-complaint | 2 | 1 | ok | root-cause-identified | no-active-incident | ✗ | — | 1 | ✓ | 2464707 | 819 | 4.79 | 1 |
| bench-v2 | claude-opus-5 | t2-quiet-d1-suggestive-complaint | 2 | 2 | ok | root-cause-identified | no-active-incident | ✗ | — | 1 | ✓ | 1860258 | 171 | 3.68 | 0 |
| bench-v2 | claude-opus-5 | t2-quiet-d1-suggestive-complaint | 2 | 3 | ok | inconclusive | no-active-incident | ✗ | — | 0 | ✓ | 2721666 | 575 | 5.15 | 0 |
| bench-v2 | claude-sonnet-5 | t2-quiet-d1-suggestive-complaint | 2 | 1 | ok | no-active-incident | no-active-incident | ✓ | — | 0 | ✓ | 4468802 | 769 | 2.36 | 6 |
| bench-v2 | claude-sonnet-5 | t2-quiet-d1-suggestive-complaint | 2 | 2 | ok | root-cause-identified | no-active-incident | ✗ | — | 1 | ✓ | 2783102 | 597 | 1.85 | 4 |
| bench-v2 | claude-sonnet-5 | t2-quiet-d1-suggestive-complaint | 2 | 3 | ok | inconclusive | no-active-incident | ✗ | — | 0 | ✓ | 3556550 | 662 | 2.01 | 5 |
| bench-v2 | claude-fable-5 | t2-red-herring-latency-latent-d1 | 2 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1662206 | 669 | 5.94 | 0 |
| bench-v2 | claude-fable-5 | t2-red-herring-latency-latent-d1 | 2 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1741186 | 349 | 6.73 | 0 |
| bench-v2 | claude-fable-5 | t2-red-herring-latency-latent-d1 | 2 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1587432 | 192 | 7.41 | 0 |
| bench-v2 | claude-opus-5 | t2-red-herring-latency-latent-d1 | 2 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 2231723 | 655 | 4.57 | 1 |
| bench-v2 | claude-opus-5 | t2-red-herring-latency-latent-d1 | 2 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 2213633 | 906 | 4.92 | 1 |
| bench-v2 | claude-opus-5 | t2-red-herring-latency-latent-d1 | 2 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 2205017 | 285 | 4.68 | 0 |
| bench-v2 | claude-sonnet-5 | t2-red-herring-latency-latent-d1 | 2 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 3727880 | 1011 | 2.50 | 3 |
| bench-v2 | claude-sonnet-5 | t2-red-herring-latency-latent-d1 | 2 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 5519175 | 1155 | 3.54 | 1 |
| bench-v2 | claude-sonnet-5 | t2-red-herring-latency-latent-d1 | 2 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 3150468 | 868 | 2.07 | 3 |
| bench-v2 | claude-fable-5 | t3-chaos-low-rate-intermittent | 3 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 898155 | 516 | 4.70 | 0 |
| bench-v2 | claude-fable-5 | t3-chaos-low-rate-intermittent | 3 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1297544 | 156 | 6.13 | 0 |
| bench-v2 | claude-fable-5 | t3-chaos-low-rate-intermittent | 3 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 647465 | 456 | 4.07 | 0 |
| bench-v2 | claude-opus-5 | t3-chaos-low-rate-intermittent | 3 | 1 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 1761243 | 220 | 3.70 | 0 |
| bench-v2 | claude-opus-5 | t3-chaos-low-rate-intermittent | 3 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1633930 | 592 | 3.50 | 1 |
| bench-v2 | claude-opus-5 | t3-chaos-low-rate-intermittent | 3 | 3 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 1858591 | 250 | 4.37 | 0 |
| bench-v2 | claude-sonnet-5 | t3-chaos-low-rate-intermittent | 3 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 2191465 | 142 | 1.52 | 0 |
| bench-v2 | claude-sonnet-5 | t3-chaos-low-rate-intermittent | 3 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 5179120 | 1109 | 2.97 | 10 |
| bench-v2 | claude-sonnet-5 | t3-chaos-low-rate-intermittent | 3 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1905211 | 474 | 1.40 | 1 |
| bench-v2 | claude-fable-5 | t3-crash-hard-down | 3 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 585606 | 368 | 3.33 | 0 |
| bench-v2 | claude-fable-5 | t3-crash-hard-down | 3 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1171353 | 131 | 3.70 | 0 |
| bench-v2 | claude-fable-5 | t3-crash-hard-down | 3 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 812607 | 421 | 3.71 | 0 |
| bench-v2 | claude-opus-5 | t3-crash-hard-down | 3 | 1 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 1762620 | 792 | 4.16 | 1 |
| bench-v2 | claude-opus-5 | t3-crash-hard-down | 3 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 1707716 | 693 | 3.78 | 0 |
| bench-v2 | claude-opus-5 | t3-crash-hard-down | 3 | 3 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 735403 | 427 | 1.74 | 1 |
| bench-v2 | claude-sonnet-5 | t3-crash-hard-down | 3 | 1 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 3105120 | 466 | 1.89 | 3 |
| bench-v2 | claude-sonnet-5 | t3-crash-hard-down | 3 | 2 | ok | root-cause-identified | root-cause-identified | ✓ | ✓ | 0 | ✓ | 3902509 | 376 | 2.02 | 2 |
| bench-v2 | claude-sonnet-5 | t3-crash-hard-down | 3 | 3 | ok | root-cause-identified | root-cause-identified | ✗ | ✗ | 0 | ✓ | 2140406 | 383 | 1.07 | 3 |
