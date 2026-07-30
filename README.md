# konan

**konan** is an agentic production-incident investigator built as Claude Code skills.
When something breaks, konan is the on-call agent: it triages, forms hypotheses, gathers
evidence, and delivers an investigation report in which every claim cites its evidence —
running on the Claude Code harness and subscription you already have.

It investigates read-only, cites evidence for every claim, and is measured by 
a seeded-fault eval harness before it is believed.

Hebrew: כונן, the on-call engineer — the role that owns an incident end to end. (Bonus:
Konan ≈ Conan, as in Doyle, the author behind the detective.

**Status: private bootstrap, pre-v0.1.** The repo flips public at v0.1, together with
the first eval scorecard.

- Product contract: [docs/product.md](docs/product.md)
- Lab target: [faultline](https://github.com/lyudmylan/faultline)
