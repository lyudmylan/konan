# Plan: the receiver of the Alertmanager webhook (#114)

Intent: `intents/alert-webhook.md`. Written 2026-11-16. Accepted by the leader in the conversation on
2026-11-22.

## Steps

1. `scripts/receive.py`, the parts that decide, as pure functions so that the pins call them without a
   socket. `read_token(path)` returns the content of the file with the whitespace at both ends removed,
   or nothing for a missing or empty file. `address(env)` returns the host and the port, `127.0.0.1` and
   `9911` without the two variables. `known_pairs(inbox)` reads the pairs of `fingerprint` and `startsAt`
   from the inbox and skips a line that does not parse; a missing inbox gives no pairs.
   `complaints(payload)` checks the whole payload first (an object with a list `alerts`; each alert an
   object with `status`, a text `fingerprint`, a text `startsAt`, and objects for `labels` and
   `annotations` when present) and raises one error for any fault, then returns the complaint objects of
   the firing alerts and the count of the resolved ones. A complaint object holds `source`,
   `fingerprint`, `labels`, `annotations`, `startsAt`, and `generatorURL` when the alert has it.
2. `scripts/receive.py`, one call. The order of the decisions: a path other than `/alerts` gets 404 and a
   method other than POST gets 405; a missing or wrong token gets 401 before the body is read; a missing
   length gets 411 and a length over 1 MiB gets 413, also before the body is read; a body that is not
   JSON or a payload with a fault gets 400. Then each firing alert in the order of the list: a known pair
   is counted; a new pair is written as one JSON line with `json.dumps` (a line break inside a text stays
   escaped), flushed and synced, and then joins the known pairs. A write error gets 500. The lines of the
   same call that were written before the error stay, and the retry of Alertmanager finds their pairs
   known. The answer 200 carries the three counts as JSON.
3. `scripts/receive.py`, the server. `http.server.HTTPServer`, which answers one call at a time in one
   thread, with a handler whose socket has a read limit of 10 seconds. The limit is an argument of the
   function that builds the server, so that a pin runs with a short one; no environment variable changes
   it. `main()` reads the token and exits with code 2 and a message when there is none, binds the address
   and exits with code 1 and a message when the port is taken, creates `alerts/` when it is missing,
   prints one start line with the address, and serves until it is interrupted. The log is one line per
   call on standard output, flushed: the time in UTC, the answer code, `new=`, `known=`, `resolved=`.
   The default handler log of the library is turned off, because it prints the request line. The file
   gets the executable bit and the line `#!/usr/bin/env python3`.
4. `scripts/tests.py`, plain asserts with the standard library, in the form of `hooks/tests.py`; each
   docstring cites the intent and the number of its check. A helper starts the server of step 3 in a
   thread on port 0 of the loopback interface with a temporary inbox and a temporary token, and a helper
   sends a call with `urllib.request`. The ten pins have the names that the intent gives:
   - `test_call_without_the_token_is_refused` (check 1): no header, a wrong token, and the scheme `Basic`
     get 401 with the inbox unchanged; a token file that ends with a line break accepts the call.
   - `test_firing_group_becomes_one_line_per_alert` (check 2): two firing alerts, one with a line break
     in an annotation and one without `generatorURL`; two lines, each parsed and compared field by field.
   - `test_repeat_adds_no_line_and_a_new_start_adds_one` (check 3): the same call twice; a second server
     on the same inbox with a line of plain text added to it; two threads that send the same new call at
     the same time; then a later `startsAt`.
   - `test_resolved_alert_adds_no_line` (check 4).
   - `test_malformed_call_writes_nothing` (check 5): the faults of step 2, each together with one valid
     firing alert where the payload allows it; a declared length over the limit; a wrong path; a GET; and
     a connection that sends its headers and no body, after which the next call is answered, with a read
     limit of half a second.
   - `test_no_token_no_listener` (check 6): the script as a process, with no token file and with an empty
     one; the exit code is 2 and a connection to the port is refused.
   - `test_default_address_is_loopback` (check 7): `address({})`.
   - `test_log_holds_no_token_and_no_body` (check 8): the captured log of one accepted call and one
     refused call.
   - `test_settings_allow_the_receiver_without_arguments` (check 9): the two entries are in the allow
     list, and no other entry of the list contains `receive.py`.
   - `test_write_failure_is_500_and_taken_port_exits` (check 10): an inbox path that is a directory gets
     500; the script as a process on a port that the test holds exits with code 1.
5. `charter.toml`: `python3 scripts/tests.py` as the third command of `checks.quality`. The workflow
   `tests` runs the commands of the contract, so no workflow file changes.
6. `.claude/settings.json`: `Bash(scripts/receive.py)` and `Bash(./scripts/receive.py)` after the
   `printenv` entry of the allow list. Nothing else in the file changes.
7. `skills/oncall/SKILL.md`. Step 1 (catch-up): a line is handled when one journal holds its
   `fingerprint` and its `startsAt`. A new step between catch-up and watch: when `alerts/receiver-token`
   exists, or the file that `KONAN_RECEIVER_TOKEN_FILE` names, start `scripts/receive.py` as a background
   command, exactly in that form; when it exits at once (no token, port taken), record that in the shift
   report and go on; without a token file start nothing. The boundaries paragraph names the receiver
   among the pre-approved actions. The description line of the skill names the webhook. Superseded in
   part: see "Changes after the code review" for the order and for the token file.
8. `docs/triggers.md`. The adapter bullet: for the HTTP transport the adapter includes one receiver
   script, `scripts/receive.py`, which runs while a shift or the operator runs it; konan has no deployed
   service. The group sentence: one alert, one investigation, with the pair as the key. Rule 5: the
   receiver drops a repeat of a pair already in the inbox, and konan keeps no other queue machinery. The
   profile bullet "lab" stays. Under "native stacks", the Alertmanager line becomes the receiver
   configuration (a `webhook_configs` entry with the address, `send_resolved: false`, and
   `http_config.authorization` with `credentials_file`) and the two limits of the intent. The Sentry
   line: its payload is not the group form; its profile delivers that form, or a later work item decides
   on a mapping. The Grafana line keeps its content.
9. `docs/architecture.md`: in the system picture, a solid edge from the stack through the receiver to the
   inbox, and the planned cloud edge stays dashed; in the on-call trigger path, the receiver as a
   participant between the alerter and the inbox, with the note that a call with no receiver is not
   stored. `docs/product.md`: the stance line on triggers names the receiver as the trigger plumbing of
   the HTTP transport, and the roadmap line on real-stack integrations says that the local alert-webhook
   trigger exists and the cloud one follows. `AGENTS.md`: one line for `scripts/receive.py` in
   "Commands", and the two entries in the sentence on unattended shift writes. `skills/README.md`: the
   line on `oncall`. The README is not changed: its sentence on the stance stays true.
10. The two commands of `AGENTS.md`, then the automatic checks 1 to 12 of the intent by hand, then the
    built-in code review on the diff, and its findings answered before the change request.
11. Manual check 13, after the code, with the leader as the operator. Alertmanager runs from its public
    container image on the operator's computer, with a configuration file outside the repository that
    names `http://host.docker.internal:9911/alerts` and a token file. The lab runs healthy. The operator
    starts `/oncall` in a new session, so that the shift is not this session. One alert is added with
    `amtool` inside the container. I read the receiver log, the journal and the shift report, and I put
    the log lines, the journal name and the two extra shift reports of the check into the change
    request. One risk, to be settled at this step: whether a container reaches a receiver that listens
    on the loopback address of this computer. If it does not, the run sets `KONAN_RECEIVER_HOST`, and the
    record says so.
12. One change request, `Closes #114`, with the rationale for the two allow entries and for the third
    quality check. `intents/**`, `charter.toml`, `AGENTS.md` and `.claude/settings.json` are in the high
    tier, so the leader merges.

## Changes after the code review

- The on-call skill: the watch starts first, then the receiver, then the catch-up. In the order of step
  7, a line that the receiver wrote before the watch started was never delivered, and its pair was
  known to the receiver from then on. This replaces the order in the intent
  (`intents/alert-webhook.md`, the scope line on `skills/oncall/SKILL.md`), which this change request
  changes to match.
- The shift looks only for `alerts/receiver-token`. It cannot read `KONAN_RECEIVER_TOKEN_FILE` without a
  permission prompt, so that variable is for a start by hand; step 7 named both. The scope line of the
  intent now says so.
- `scripts/receive.py` reads the pairs again when the inbox was changed from outside, so that a pair is
  known only while its line is in the inbox.
- `scripts/receive.py` holds a lock file, `alerts/receiver.lock`, for the life of the process. On macOS a
  receiver on the loopback address and one on all addresses can bind the same port, so the taken port
  alone did not stop a second receiver.
- The token is compared as bytes, so a token outside ASCII matches; a byte order mark in the token file
  is ignored. A length that is not a number of ASCII digits gets 411. The answers of the library (a bad
  request line, a method with no handler) get a log line, and the log line is written before the answer.
- `docs/triggers.md`: a third limit, a refused call is not sent again.
- The pins for these, all in `scripts/tests.py`, each inside a test that the intent names. The pairs
  read again: `test_repeat_adds_no_line_and_a_new_start_adds_one` (an emptied inbox makes a pair new, a
  line from another writer makes a pair known). The lock file:
  `test_write_failure_is_500_and_taken_port_exits` (a second hold of the same inbox gets none). The
  token as bytes and the byte order mark: `test_call_without_the_token_is_refused`. The 411 and the log
  lines for the answers of the library: `test_malformed_call_writes_nothing`. The order of the log line
  and the answer has no pin: a test cannot see it without a fault in the connection.
- Two additions to the intent, accepted by the leader in the conversation on 2026-11-22. The deny list
  of `.claude/settings.json` gets `Read(./alerts/receiver-token)` and `Read(/alerts/receiver-token)`, so
  that the secrecy of the token does not rest on a sentence of the skill. The rule covers the file tools
  and the file commands that the harness recognizes in a Bash command; a script that reads the file is
  not covered (the permissions page of the harness, read on 2026-11-22). `scripts/receive.py` joins
  `tiers.high.paths` of `charter.toml`, as `scripts/probe.sh` is, because a shift runs it without a
  prompt.

## Changes after the live run

The live run of check 13 on 2026-11-24 led to two changes.

- `skills/oncall/SKILL.md`, the catch-up step: the search for the pair is named as plain commands, one
  value per call. In three of three shift starts the shift wrote one command with a loop and a shell
  variable, and that command needed a permission. With the new sentence a fourth start asked for none.
- `docs/triggers.md`: the lock file stays after the receiver ends and blocks nothing. Two shifts of the
  run took the file for a lock that nobody holds.

## Files

New: `scripts/receive.py`, `scripts/tests.py`, this plan, the journal of the live run. Changed: `charter.toml`,
`.claude/settings.json`, `skills/oncall/SKILL.md`, `skills/README.md`, `docs/triggers.md`,
`docs/architecture.md`, `docs/product.md`, `AGENTS.md`. Not changed: `hooks/boundary.py`,
`hooks/tests.py`, `scripts/alert.sh`, the investigate skill, the README.

## What I will not do

No thread per call, no queue, no retry, no state file: the inbox is the only memory, and the lock file
holds no content. No option on the
command line: the allow entries are exact. No change to the complaint object.
