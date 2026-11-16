# konan scorecard

Generated 2026-11-15T17:35:49+02:00 — 30 scenario(s) scored, model(s): claude-fable-5-2.
Deterministic scoring (regex + equality only); semantics: `eval/README.md`.

## Summary

- **Scenarios passed: 16/30**
- Root-cause accuracy: 9/21 (scenarios expecting a root cause)
- False attributions: 2
- Evidence-citation compliance: 30/30
- Tokens: 42341897
- Wall clock: 8139s total

## Scenarios

| Scenario | Model | Verdict | Class | Root cause | False attr | Citations | Tokens | Wall (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chaos-error-rate | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1302649 | 216 |
| chaos-error-rate | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1521529 | 361 |
| chaos-error-rate | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1605937 | 233 |
| chaos-latency | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1046257 | 293 |
| chaos-latency | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1241320 | 229 |
| chaos-latency | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1324906 | 316 |
| d1-zero-stock-product-page | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1544956 | 243 |
| d1-zero-stock-product-page | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1553185 | 341 |
| d1-zero-stock-product-page | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1611829 | 216 |
| d2-null-price-order | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 2046578 | 366 |
| d2-null-price-order | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1476759 | 277 |
| d2-null-price-order | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1577057 | 245 |
| healthy-baseline | claude-fable-5-2 | ✓ no-active-incident | — | — | 0 | ✓ | 1641300 | 225 |
| healthy-baseline | claude-fable-5-2 | ✓ no-active-incident | — | — | 0 | ✓ | 1157366 | 167 |
| healthy-baseline | claude-fable-5-2 | ✓ no-active-incident | — | — | 0 | ✓ | 1613909 | 271 |
| t2-healthy-after-chaos-window | claude-fable-5-2 | ✓ no-active-incident | — | — | 0 | ✓ | 1496560 | 228 |
| t2-healthy-after-chaos-window | claude-fable-5-2 | ✓ no-active-incident | — | — | 0 | ✓ | 1173302 | 235 |
| t2-healthy-after-chaos-window | claude-fable-5-2 | ✓ no-active-incident | — | — | 0 | ✓ | 1488649 | 363 |
| t2-quiet-d1-suggestive-complaint | claude-fable-5-2 | ✗ root-cause-identified (want no-active-incident) | — | — | 1 | ✓ | 1470233 | 212 |
| t2-quiet-d1-suggestive-complaint | claude-fable-5-2 | ✓ no-active-incident | — | — | 0 | ✓ | 1628916 | 333 |
| t2-quiet-d1-suggestive-complaint | claude-fable-5-2 | ✗ root-cause-identified (want no-active-incident) | — | — | 1 | ✓ | 1780856 | 424 |
| t2-red-herring-latency-latent-d1 | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1861032 | 476 |
| t2-red-herring-latency-latent-d1 | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1474477 | 212 |
| t2-red-herring-latency-latent-d1 | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1160218 | 251 |
| t3-chaos-low-rate-intermittent | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1235323 | 230 |
| t3-chaos-low-rate-intermittent | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1351104 | 290 |
| t3-chaos-low-rate-intermittent | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1253075 | 295 |
| t3-crash-hard-down | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 939791 | 198 |
| t3-crash-hard-down | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 859827 | 184 |
| t3-crash-hard-down | claude-fable-5-2 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 902997 | 209 |

## Failure detail

### chaos-error-rate

- must_claim `switch-flipped`: no match in the claim surface
- must_claim `spread`: no match in the claim surface

### chaos-error-rate

- must_claim `switch-flipped`: no match in the claim surface

### chaos-error-rate

- must_claim `switch-flipped`: no match in the claim surface
- must_claim `spread`: no match in the claim surface

### chaos-latency

- must_claim `switch-flipped`: no match in the claim surface

### chaos-latency

- must_claim `switch-flipped`: no match in the claim surface

### chaos-latency

- must_claim `switch-flipped`: no match in the claim surface

### t2-quiet-d1-suggestive-complaint

- verdict: got `root-cause-identified`, want `no-active-incident`
- cause: got `unhandled-exception`, want `None` — false attribution

### t2-quiet-d1-suggestive-complaint

- verdict: got `root-cause-identified`, want `no-active-incident`
- cause: got `unhandled-exception`, want `None` — false attribution

### t2-red-herring-latency-latent-d1

- must_claim `switch-flipped`: no match in the claim surface

### t2-red-herring-latency-latent-d1

- must_claim `switch-flipped`: no match in the claim surface

### t2-red-herring-latency-latent-d1

- must_claim `switch-flipped`: no match in the claim surface

### t3-chaos-low-rate-intermittent

- must_claim `switch-flipped`: no match in the claim surface

### t3-chaos-low-rate-intermittent

- must_claim `switch-flipped`: no match in the claim surface
- must_claim `rare-but-real`: no match in the claim surface

### t3-chaos-low-rate-intermittent

- must_claim `switch-flipped`: no match in the claim surface
- must_claim `rare-but-real`: no match in the claim surface
