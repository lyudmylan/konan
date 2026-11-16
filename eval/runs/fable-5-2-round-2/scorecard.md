# konan scorecard

Generated 2026-11-16T01:01:05+02:00 — 30 scenario(s) scored, model(s): claude-fable-5-2.
Deterministic scoring (regex + equality only); semantics: `eval/README.md`.

## Summary

- **Scenarios passed: 29/30**
- Root-cause accuracy: 21/21 (scenarios expecting a root cause)
- False attributions: 1
- Evidence-citation compliance: 30/30
- Tokens: 42079617
- Wall clock: 10951s total

## Scenarios

| Scenario | Model | Verdict | Class | Root cause | False attr | Citations | Tokens | Wall (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chaos-error-rate | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1528275 | 324 |
| chaos-error-rate | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1546729 | 238 |
| chaos-error-rate | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1097877 | 248 |
| chaos-latency | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1274385 | 227 |
| chaos-latency | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1121918 | 200 |
| chaos-latency | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1178214 | 250 |
| d1-zero-stock-product-page | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1697395 | 248 |
| d1-zero-stock-product-page | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1447464 | 282 |
| d1-zero-stock-product-page | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1443791 | 329 |
| d2-null-price-order | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1093107 | 251 |
| d2-null-price-order | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1434300 | 275 |
| d2-null-price-order | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1429439 | 245 |
| healthy-baseline | claude-fable-5-2 | ✓ no-active-incident | — | — | 0 | ✓ | 1348793 | 272 |
| healthy-baseline | claude-fable-5-2 | ✓ no-active-incident | — | — | 0 | ✓ | 1228049 | 220 |
| healthy-baseline | claude-fable-5-2 | ✓ no-active-incident | — | — | 0 | ✓ | 1627495 | 299 |
| t2-healthy-after-chaos-window | claude-fable-5-2 | ✓ no-active-incident | — | — | 0 | ✓ | 1435386 | 222 |
| t2-healthy-after-chaos-window | claude-fable-5-2 | ✓ no-active-incident | — | — | 0 | ✓ | 1463007 | 278 |
| t2-healthy-after-chaos-window | claude-fable-5-2 | ✓ no-active-incident | — | — | 0 | ✓ | 1429524 | 300 |
| t2-quiet-d1-suggestive-complaint | claude-fable-5-2 | ✗ root-cause-identified (want no-active-incident) | — | — | 1 | ✓ | 1746650 | 321 |
| t2-quiet-d1-suggestive-complaint | claude-fable-5-2 | ✓ no-active-incident | — | — | 0 | ✓ | 1596330 | 363 |
| t2-quiet-d1-suggestive-complaint | claude-fable-5-2 | ✓ no-active-incident | — | — | 0 | ✓ | 1532451 | 279 |
| t2-red-herring-latency-latent-d1 | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1491354 | 309 |
| t2-red-herring-latency-latent-d1 | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 2006182 | 457 |
| t2-red-herring-latency-latent-d1 | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1394784 | 1286 |
| t3-chaos-low-rate-intermittent | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1488182 | 2118 |
| t3-chaos-low-rate-intermittent | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1266438 | 218 |
| t3-chaos-low-rate-intermittent | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1575176 | 244 |
| t3-crash-hard-down | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1167859 | 221 |
| t3-crash-hard-down | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 942656 | 205 |
| t3-crash-hard-down | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1046407 | 222 |

## Failure detail

### t2-quiet-d1-suggestive-complaint

- verdict: got `root-cause-identified`, want `no-active-incident`
- cause: got `unhandled-exception`, want `None` — false attribution
