# Intent: the receiver of the Alertmanager webhook

Work item: #114. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

An Alertmanager webhook call to an address on the operator's computer becomes one line per new firing alert
in the alert inbox, with the origin of the call verified by a token, and the on-call shift investigates
each line as it does today.

## In scope

- The form, decided with the leader on 2026-11-16: a receiver script, `scripts/receive.py`, Python with
  the standard library only. The on-call shift starts it, and the operator can start it by hand. It
  writes the durable inbox `alerts/inbox.jsonl` that the shift already watches, so a line waits for a
  session that reads it. The other candidate was a channel of the harness. It is a research preview, a
  channel of our own loads only with a development flag, and a call that arrives with no open session is
  lost (the channels reference of the harness, read on 2026-11-16).
- `scripts/receive.py`, the address. It listens for `POST /alerts` on `127.0.0.1:9911`.
  `KONAN_RECEIVER_HOST` and `KONAN_RECEIVER_PORT` change the address; the default accepts calls from the
  same computer only. A host other than loopback sends the token in clear text; the Alertmanager line of
  `docs/triggers.md` states that limit. A port that is taken ends the script with a message and a
  non-zero exit. A second receiver on the same inbox ends the script in the same way; the lock file
  `alerts/receiver.lock` holds no content.
- `scripts/receive.py`, the origin. The token is the content of the file `alerts/receiver-token`
  (`alerts/` is ignored by git), or of the file that `KONAN_RECEIVER_TOKEN_FILE` names, with the
  whitespace at both ends removed; a file that is empty after that counts as empty. Without a token
  file, or with an empty one, the script does not listen. A call carries `Authorization: Bearer <token>`,
  which Alertmanager sends from `http_config.authorization`. The comparison takes constant time. A call
  without the token gets 401 and writes nothing.
- `scripts/receive.py`, the payload. It accepts the native webhook payload of Alertmanager: a group with
  a list `alerts`. Each alert of the list with the status `firing` becomes one complaint object of
  `docs/triggers.md`: `source` is `alert`, and `fingerprint`, `labels`, `annotations`, `startsAt` and
  `generatorURL` are copied as they came. The object is one JSON line, appended and synced to disk before
  the answer 200. A body over 1 MiB, a body that is not JSON, a payload without the list, or an alert
  without `fingerprint` or `startsAt` gets an answer in the 400 range, and the call writes nothing. A
  write that fails gets 500, so the retry of Alertmanager delivers the call again.
- The rule for a group, a repeat, and a resolved alert. One alert is one line and one investigation; the
  complaint contract keeps its single-alert shape. The key of an alert is the pair of `fingerprint` and
  `startsAt`, because Alertmanager derives the fingerprint from the labels, and the same alert that fires
  again later carries the same fingerprint with a new `startsAt`. A call that repeats a pair already in
  the inbox adds no line. The inbox is the only memory of the pairs: the script reads them from the inbox
  when it starts, and again when another writer changed the inbox, and skips a line that does not parse. An alert with the status `resolved` adds no line.
  Both get 200. The number of investigations for one incident follows from the routing and the inhibition
  rules of the stack.
- The stance "adding a stack costs a profile, never code" of `docs/product.md` and `docs/triggers.md`
  stays. The receiver is the adapter for the HTTP transport, written once. It takes the group form of the
  shape that the complaint contract adopted, and it holds no mapping for a stack. The decision record of
  the trigger epic (#4) says that Grafana Alerting emits the same alert fields. A stack with another
  payload is out of this work item: its profile delivers the group form of the contract, or a later work
  item decides on its mapping. The Sentry line of `docs/triggers.md`, which today says that the adapter
  executes a mapping, is changed to say so. The two documents name the receiver where they state the
  stance.
- `scripts/receive.py`, one call at a time. The script answers calls one after the other, in one thread,
  so the test of a pair and the append of its line are one step. A read that takes more than 10 seconds
  is closed with no line written, so a connection that sends nothing does not hold the next call.
- `scripts/receive.py`, the log: one line per call with the time, the answer code and the three counts
  (new, known, resolved). The token and the body of a call are never logged.
- `skills/oncall/SKILL.md`. When the token file `alerts/receiver-token` exists, the shift starts the
  receiver as a background command after the watch of the inbox has started; without the file the shift
  is the lab profile of today. The shift looks for that file only: a file that
  `KONAN_RECEIVER_TOKEN_FILE` names is for a start by hand. A receiver
  that does not start is recorded in the shift report, and the shift watches the inbox. The catch-up step
  treats a line as handled when one journal holds its `fingerprint` and its `startsAt`.
- `.claude/settings.json`: two entries in the allow list, `Bash(scripts/receive.py)` and
  `Bash(./scripts/receive.py)`, exact, with no argument form, so that an unattended shift starts the
  receiver without a prompt; and two entries in the deny list, `Read(./alerts/receiver-token)` and
  `Read(/alerts/receiver-token)`, so that the secrecy of the token does not rest on a sentence of the
  skill. The rationale for the allow entries, for the change request: the script takes no argument, reads its
  configuration from the environment and one file, opens one listening port, and sends nothing. The
  boundary hook and its allow shapes do not change.
- `scripts/tests.py`: the pins of the checks below, each against a receiver on a free port of the loopback
  interface with a temporary inbox. `charter.toml`: `python3 scripts/tests.py` joins `checks.quality`. `scripts/receive.py` joins
  `tiers.high.paths`, as `scripts/probe.sh` is, because a shift runs it without a prompt.
- `docs/triggers.md`: the adapter paragraph says what the receiver is (one script that runs while a shift
  or the operator runs it, no deployed service); the group sentence states the rule above; rule 5 states
  that the receiver drops a repeat of a pair already in the inbox, and that konan keeps no other queue
  machinery; under "native stacks", the Alertmanager line is replaced by the receiver configuration with
  the address and `credentials_file`, its sentence on sender-side templating is removed because the
  receiver takes the native payload, and the line states three limits: a call that finds no receiver is not
  stored by konan, and Alertmanager sends a firing alert again after its repeat interval; a host other
  than loopback sends the token in clear text; a refused call is not sent again. `docs/architecture.md`: the receiver in the system picture
  and in the on-call trigger path. `docs/product.md`: the roadmap line on alert-webhook triggers, and the
  stance line on triggers, which names the receiver as the trigger plumbing of the HTTP transport.
  `AGENTS.md`: the command in "Commands", and the new allow entries in the sentence on unattended shift
  writes. `skills/README.md`: the line on `oncall`.

## Out of scope

One investigation for a whole group: it needs a complaint object that holds several alerts, which is a
change to the complaint contract. A link between investigations of the same incident (#28). The cloud
routine adapter (#35). The receiver in a plugin install: this work item covers a checkout of this repo.
TLS on the receiver. Sending the result of an investigation to an address. Behavior that depends on
severity (#29). Profiles for other stacks. The boundary hook, its pins and its allow shapes.

## Acceptance checks

## Automatic checks

1. A call without the header, and a call with a wrong token, get 401, and the inbox does not change. With
   a token file that ends with a line break, a call with the token is accepted.
   test: `scripts/tests.py::test_call_without_the_token_is_refused`. command: `python3 scripts/tests.py`
2. A call with a group of two firing alerts gets 200 and adds two lines. Each line is one JSON object with
   `source` equal to `alert` and with `fingerprint`, `labels`, `annotations`, `startsAt` and
   `generatorURL` equal to the values of the call. An annotation that holds a line break stays inside its
   one line.
   test: `scripts/tests.py::test_firing_group_becomes_one_line_per_alert`
3. The same call a second time gets 200 and adds no line, also after the receiver restarts on the same
   inbox, and also when the inbox holds a line that does not parse. Two identical calls that are sent at
   the same time add one line. A call with the same fingerprint and a later `startsAt` adds one line.
   A line that another writer appends to the inbox makes its pair known; an emptied inbox makes it new.
   test: `scripts/tests.py::test_repeat_adds_no_line_and_a_new_start_adds_one`
4. A call with the status `resolved` gets 200 and adds no line. A call that holds one firing alert and
   one resolved alert adds one line.
   test: `scripts/tests.py::test_resolved_alert_adds_no_line`
5. A body that is not JSON, a payload without the list `alerts`, an alert without `fingerprint`, an alert without `startsAt`, and a
   body over the size limit each get an answer in the 400 range, and the inbox does not change, also for
   the valid alerts of the same call. A path other than `/alerts` and a method other than POST write
   nothing. A connection that sends no body does not block the next call: the test runs with a short
   read limit.
   test: `scripts/tests.py::test_malformed_call_writes_nothing`
6. Without a token file, and with an empty one, the script exits with a non-zero code and opens no port.
   test: `scripts/tests.py::test_no_token_no_listener`
7. Without `KONAN_RECEIVER_HOST` the receiver binds the loopback address.
   test: `scripts/tests.py::test_default_address_is_loopback`
8. The log of a call holds the answer code and the counts, and holds neither the token nor the summary
   text of the alert.
   test: `scripts/tests.py::test_log_holds_no_token_and_no_body`
9. The allow list of `.claude/settings.json` holds the two exact entries and no entry for the receiver
   with an argument form, and the deny list holds the two read entries of the token file.
   test: `scripts/tests.py::test_settings_allow_the_receiver_without_arguments`
10. A write to the inbox that fails gets 500 and adds no line. With the port taken, the script exits with
    a non-zero code. A second hold of the lock of one inbox gets none. The sync to disk before the answer has no check: a test cannot observe it without a
    fault in the file system, and the code review reads it.
    test: `scripts/tests.py::test_write_failure_is_500_and_taken_port_exits`
11. A document check, of words and not of behavior: the shift skill names the receiver and the pair, and
    the trigger contract names the receiver and the token file setting. Manual check 13 covers the
    behavior of the shift.
    command: `grep -q 'scripts/receive.py' skills/oncall/SKILL.md && grep -q 'startsAt' skills/oncall/SKILL.md && grep -q 'scripts/receive.py' docs/triggers.md && grep -q 'credentials_file' docs/triggers.md`
12. The quality checks, with `python3 scripts/tests.py` among them, and the contract checks pass.
    command: `grep -q 'python3 scripts/tests.py' charter.toml && charter-gate quality --contract charter.toml && charter-check all charter.toml`

## Manual checks

13. With an Alertmanager on the operator's computer that names the address and the token file, and an
    on-call shift on the lab: a firing alert leads to a committed journal whose complaint block holds the
    fingerprint and the `startsAt` of the alert, the shift started the receiver without a permission
    prompt, and a repeated call of the same alert leads to no second journal. Two more shift starts:
    with the token file and the port taken, the shift report records that the receiver did not start, and
    the shift watches the inbox; with no token file, the shift starts no receiver and watches the inbox.
    The change request records the receiver log lines, the journal name and the two shift reports. who: the engineer runs it, the leader reads the record.
    Not automatic: it needs a running Alertmanager and the lab, and the investigation calls the model.
