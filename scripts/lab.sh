#!/bin/sh
# Run faultline as konan's lab target. Runtime artifacts live under lab/
# (gitignored): logs in lab/logs (via FAULTLINE_LOG_DIR), pid file and server
# stdout beside them. Needs a faultline checkout; FAULTLINE_DIR defaults to a
# sibling of this repo.
set -eu
here="$(cd "$(dirname "$0")/.." && pwd)"
FAULTLINE_DIR="${FAULTLINE_DIR:-$here/../faultline}"
PORT="${KONAN_LAB_PORT:-8000}"
LAB="$here/lab"; LOGS="$LAB/logs"; PIDFILE="$LAB/faultline.pid"; OUT="$LAB/server.out"
UV="${UV:-uv}"
if ! command -v "$UV" >/dev/null 2>&1; then
  for c in "$HOME/.local/bin/uv" /opt/homebrew/bin/uv /usr/local/bin/uv; do
    if [ -x "$c" ]; then UV="$c"; break; fi
  done
fi

alive() { [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; }
healthy() { curl -fsS --max-time 2 "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; }

case "${1:?usage: scripts/lab.sh start|stop|status}" in
  start)
    if alive && healthy; then echo "lab: already running (pid $(cat "$PIDFILE"))"; exit 0; fi
    if ! alive && healthy; then
      echo "lab: something lab.sh does not own already serves :$PORT — refusing to adopt it" >&2
      echo "lab: stop it yourself, or use KONAN_LAB_PORT to pick another port" >&2
      exit 1
    fi
    [ -d "$FAULTLINE_DIR" ] || { echo "lab: no faultline checkout at $FAULTLINE_DIR (set FAULTLINE_DIR)" >&2; exit 1; }
    mkdir -p "$LOGS"
    (cd "$FAULTLINE_DIR" && HOST=127.0.0.1 PORT="$PORT" FAULTLINE_LOG_DIR="$LOGS" \
      nohup "$UV" run faultline >"$OUT" 2>&1 & echo $! >"$PIDFILE")
    i=0
    while [ $i -lt 20 ]; do
      sleep 1
      if healthy; then
        # uv wraps the real server; record the child too so stop can kill both.
        pgrep -P "$(cat "$PIDFILE")" 2>/dev/null >>"$PIDFILE" || true
        echo "lab: faultline up on :$PORT (pids $(tr '\n' ' ' <"$PIDFILE"), logs in lab/logs/)"; exit 0
      fi
      i=$((i + 1))
    done
    echo "lab: did not become healthy in 20s; see $OUT" >&2; exit 1 ;;
  stop)
    if [ -f "$PIDFILE" ]; then
      while read -r p; do kill "$p" 2>/dev/null || true; done <"$PIDFILE"
    fi
    # Graceful shutdown takes a moment — verify death instead of declaring it.
    i=0
    while [ $i -lt 10 ]; do
      if ! healthy; then rm -f "$PIDFILE"; echo "lab: stopped"; exit 0; fi
      sleep 1; i=$((i + 1))
    done
    echo "lab: still serving :$PORT after 10s — not stopped (pids: $(tr '\n' ' ' <"$PIDFILE" 2>/dev/null))" >&2
    exit 1 ;;
  status)
    if healthy; then echo "lab: running on :$PORT (healthy)"
    elif alive; then echo "lab: process alive but /health not responding (crashed or hung?)"
    else echo "lab: not running"; fi ;;
  *) echo "usage: scripts/lab.sh start|stop|status" >&2; exit 2 ;;
esac
