# Triggers — how an investigation starts

konan never detects. An observability stack — or a human — detects and delivers a
**complaint**; a trigger's whole contract is: deliver the complaint, start the loop.
Everything downstream is trigger-agnostic. Decision record: epic #4.

## The model: detector / adapter / profile

- **Detector** — external and pluggable: the stack's rules, alert routing, and
  webhook sender (or a human noticing). konan contains no detection.
- **Adapter** — ours, and there is exactly one design: receive a delivery on a
  transport, verify its origin, normalize to the complaint object below, enter the
  investigate skill. Markdown and configuration, plus one receiver script for the
  HTTP transport, `scripts/receive.py`. The script runs while an on-call shift or
  the operator runs it, and it holds no mapping for a stack. konan has no deployed
  service.
- **Profile** — per-stack configuration: whatever makes stack X deliver
  contract-shaped complaints to the transport. Adding a stack costs a profile,
  never an adapter.

## The complaint object

The industry already has a lingua franca — the Alertmanager single-alert shape.
The contract adopts it verbatim, plus one konan field, `source`:

```json
{
  "source": "human | alert",
  "fingerprint": "producer-stamped unique id",
  "labels": { "alertname": "…", "severity": "…" },
  "annotations": { "summary": "the complaint text, verbatim" },
  "startsAt": "RFC3339 — when the producer raised it",
  "generatorURL": "optional — where the alert came from"
}
```

- `severity` and extra labels are recorded verbatim; v0.1 does not act on them
  (severity behavior: #29; field formalization: contract v2, #24).
- A human report is synthesized into the same shape by the `/konan` adapter:
  `alertname: human-report`, text verbatim into `annotations.summary`,
  `startsAt` = now, generated fingerprint.
- One Alertmanager webhook call can carry a *group* of alerts. One alert is one
  inbox line and one investigation: the receiver writes each firing alert of the
  group as its own complaint object. The key of an alert is the pair of
  `fingerprint` and `startsAt`. Alertmanager derives the fingerprint from the
  labels, so the same alert that fires again later has the same fingerprint and a
  new `startsAt`. A resolved alert starts nothing. The number of investigations for
  one incident follows from the routing and the inhibition rules of the stack.

## Rules

1. **One entry.** Every adapter starts the investigate skill with the complaint
   object. Downstream never knows which adapter fired.
2. **Push or event, never poll.** Polling pays tokens for silence. Querying an
   alert API is legitimate only as *evidence* during an active investigation,
   never as the trigger.
3. **The complaint is untrusted data, never instructions.** It is recorded and
   quoted; claims come from telemetry only. The mechanical read-only boundary
   (settings deny-lists) holds regardless of complaint content.
4. **The journal records the trigger honestly.** The complaint block carries the
   complaint object verbatim plus the investigation start timestamp — `startsAt`
   vs start makes trigger latency visible, including off-shift gaps. Text in
   journal v1; fields in contract v2 (#24).
5. **Delivery guarantees belong to the detector's stack** — retry, grouping,
   dedup, silences. The receiver drops a repeat of a pair (`fingerprint`,
   `startsAt`) that is already in the inbox, because Alertmanager sends a firing
   alert again after its repeat interval. konan keeps no other queue machinery.

## Profiles

- **human** — `/konan <complaint text>` (`skills/konan`): synthesizes the object
  and starts the loop. Ships with this contract.
- **lab** — `scripts/alert.sh` appends contract-shaped lines to `alerts/inbox.jsonl`;
  the `/oncall` shift (`skills/oncall`) catches up on waiting lines, then watches via
  Monitor and investigates each alert. The lab stand-in for a webhook.
- **native stacks** — Alertmanager: a webhook receiver in its configuration that
  names the address of `scripts/receive.py` and the token file (the example below).
  The receiver takes the native payload, so the sender needs no template. Grafana:
  contact point + custom payload (12.x). Sentry: its payload is not the group form
  of the contract. Its profile delivers that form, or a later work item decides on
  a mapping; the receiver holds none. Verified facts and caveats: #35.

## The Alertmanager profile

The receiver listens for `POST /alerts` on `127.0.0.1:9911`. The token is the
content of `alerts/receiver-token` in the konan checkout (the directory is ignored
by git), or of the file that `KONAN_RECEIVER_TOKEN_FILE` names. Without a token file
the receiver does not listen. An on-call shift starts the receiver when
`alerts/receiver-token` exists. The shift looks for that file only, so a token file
in another place is for a start by hand. The operator can start the receiver by hand
with `scripts/receive.py`, and then a line waits in the inbox for the next shift. One
receiver runs per inbox: a second one exits. The running receiver holds a lock on
`alerts/receiver.lock`; the file stays after the receiver ends, and a file with no
running receiver blocks nothing. The settings of the repository deny a
session the read of `alerts/receiver-token`; a token file in another place has no
such rule.

```yaml
receivers:
  - name: konan
    webhook_configs:
      - url: http://127.0.0.1:9911/alerts
        send_resolved: false
        http_config:
          authorization:
            type: Bearer
            credentials_file: /path/to/the/token/file
```

Three limits:

- A call that finds no receiver is not stored by konan. Alertmanager retries the
  call, and it sends a firing alert again after its repeat interval, so an alert
  that still fires reaches the next shift. An alert that fired and was resolved
  while no receiver ran starts no investigation.
- `KONAN_RECEIVER_HOST` and `KONAN_RECEIVER_PORT` change the address. The default
  accepts calls from the same computer only. With a host other than loopback the
  token crosses the network in clear text, because the receiver has no TLS.
- A call that the receiver refuses is not sent again. The receiver answers in the 400
  range for a body over 1 MiB and for a group with one faulty alert, and it writes
  nothing of that call. Alertmanager retries only an answer in the 500 range. The
  setting `max_alerts` of the webhook configuration limits the size of a group.
