#!/usr/bin/env bash
# Repo gate for backlog.works. Run before every commit/handoff.
# Stdlib/coreutils only. Exit non-zero on the first failing group.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
fail=0

echo "== backlog format"
python3 -W error scripts/check_backlog.py docs/product/backlog.md || fail=1

echo "== python compiles"
python3 -W error -m py_compile $(find src scripts -name '*.py') && echo "ok py_compile" || fail=1

echo "== architecture"
python3 -W error scripts/check_architecture.py || fail=1

echo "== unit tests"
PYTHONPATH=src python3 -W error -m unittest discover -s tests -t . 2>&1 | tail -3 | sed 's/^/  /'
PYTHONPATH=src python3 -W error -m unittest discover -s tests -t . >/dev/null 2>&1 && echo "ok unittest" || fail=1

echo "== app smoke test"
port=$(python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1]);s.close()')
PORT="$port" PYTHONPATH=src python3 -m backlogworks >/dev/null 2>&1 &
pid=$!
trap 'kill "$pid" 2>/dev/null || true' EXIT
ok=0
for _ in $(seq 1 20); do
  if body=$(curl -s --max-time 2 "http://127.0.0.1:$port/healthz" 2>/dev/null) && [[ "$body" == "ok" ]]; then ok=1; break; fi
  sleep 0.25
done
root=$(curl -s -o /dev/null -w '%{http_code}' --max-time 2 "http://127.0.0.1:$port/" || echo 000)
head=$(curl -sI -o /dev/null -w '%{http_code}' --max-time 2 "http://127.0.0.1:$port/healthz" || echo 000)
nf=$(curl -s -o /dev/null -w '%{http_code}' --max-time 2 "http://127.0.0.1:$port/nope" || echo 000)
gone=$(curl -s -o /dev/null -w '%{http_code}' --max-time 2 "http://127.0.0.1:$port/demo" || echo 000)
markdown=$(curl -s -o /dev/null -w '%{http_code}' --max-time 2 "http://127.0.0.1:$port/backlog.md" || echo 000)
if [[ $ok == 1 && $root == 200 && $head == 200 && $nf == 404 && $gone == 404 && $markdown == 200 ]]; then
  echo "ok smoke: /healthz=ok GET/=200 HEAD/healthz=200 /nope=404 /demo=404 /backlog.md=200"
else
  echo "FAIL smoke: healthz_ok=$ok root=$root head=$head notfound=$nf gone=$gone markdown=$markdown"; fail=1
fi
kill "$pid" 2>/dev/null || true; trap - EXIT

echo "== skills wiring"
for link in .claude/skills/*; do
  name=$(basename "$link")
  if [[ ! -L "$link" ]]; then echo "FAIL $link is not a symlink into .agents/skills"; fail=1; continue; fi
  target=".agents/skills/$name/SKILL.md"
  [[ -f "$target" ]] || { echo "FAIL $target missing"; fail=1; continue; }
  grep -q '^name: ' "$target" && grep -q '^description: ' "$target" || { echo "FAIL $target lacks name/description frontmatter"; fail=1; }
done
for d in .agents/skills/*/; do
  name=$(basename "$d")
  [[ -L ".claude/skills/$name" ]] || { echo "FAIL .claude/skills/$name link missing"; fail=1; }
done
[[ $fail == 0 ]] && echo "ok skills: $(ls .agents/skills | wc -l) skills linked"

echo "== secrets hygiene"
if grep -rnE '(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"?\s*(token|secret|password)|RAILWAY_TOKEN=[^"$(])' --include='*.md' --include='*.py' --include='*.sh' --include='*.json' . --exclude-dir=.git --exclude=check.sh; then
  echo "FAIL possible secret literal above"; fail=1
else
  echo "ok no secret-looking literals"
fi

echo
if [[ $fail == 0 ]]; then echo "CHECK PASS"; else echo "CHECK FAIL" >&2; exit 1; fi
