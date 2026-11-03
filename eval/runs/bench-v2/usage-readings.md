# Usage readings — bench-v2 (manual check 11 of intents/bench-v2-rerun.md)

The leader reads the usage panel of the subscription and states the numbers in the conversation; the
engineer records them here with the batch. The five-hour window no longer exists (dissolved by the
provider before this round); the weekly meters are the limit. The week resets on Mondays at 22:00
(Asia/Jerusalem).

| Date (local) | Moment | Model | Runs of the model so far | Week | Fable week |
| --- | --- | --- | --- | --- | --- |
| 2026-11-02 | before the first batch | claude-fable-5 | 0 | 15% | 29% |
| 2026-11-02 | after batch 1 (ten runs) | claude-fable-5 | 10 | 22% | 42% |
| 2026-11-02 | before the first batch | claude-sonnet-5 | 0 | 22% | 42% |
| 2026-11-03 | after Sonnet batch 3 and Opus batch 1 | claude-sonnet-5, claude-opus-5 | 30, 10 | 28% | 43% |
| 2026-11-03 | after Opus batch 3 and Fable batch 3, the last batch of the round | claude-opus-5, claude-fable-5 | 30, 30 | 43% | 65% |

No reading was taken between the last Sonnet batch and the first Opus batch: the batches ran in the
night without the leader. The row of 2026-11-03 is the first reading after both; it covers forty runs
of the two models together.

No reading was taken between Opus batch 1 and the last batch: the row of 43 and 65 percent covers
forty runs, twenty Opus and twenty Fable, together with the orchestrating session, which is a
Fable session on the same meters. Over the whole round the week meter went from 15 to 43 percent
and the Fable-week meter from 29 to 65 percent, for ninety investigations and the session.
