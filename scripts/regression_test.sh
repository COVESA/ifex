#!/bin/sh

# (C) 2022 Novaspring AB
# License: According to the project it is embedded in, otherwise MPL-2.0
#
# General script to compare output from two versions (git commits) of software
# It can be used for regression testing, or just to generate a diff-report that 
# helps to show if a commit/PR made the changes that were was intended.

# FUNCTIONS

fail() {
   echo "Failed. Stop. Message may follow:" 1>&2
   echo "$1" 1>&2
   exit 2;
}

cleanup() {
   rm -f /tmp/{from,to}.$$
   git worktree remove -f _worktree.tmp 2>/dev/null
}

# SETUP

cd "$(dirname "$0")/.."
PROJDIR="$PWD"

[ -d .git ] || { echo "BUG" && exit 1 ; }

# Versions to compare
from="$1"
to="$2"
script="$3"
[ $# -lt 3 ] && { echo "Usage: $0 <from-commit> <to-commit> <script-giving-output>" 1>&2 ; exit 1 ;}

# Resolve commit now because HEAD may later change
from_actual="$(git rev-parse $from)"
to_actual="$(git rev-parse $to)"

# Use current process script, not what will be checked out in worktrees
set -e
process="$(readlink -f $script)"
set +e

echo "Comparing output from $process for commits $from to $to ..." 1>&2

# MAIN

# Just in case
cd "$PROJDIR"
git worktree remove -f _worktree.tmp 2>/dev/null

# Process using new version (to)
git worktree add -ff _worktree.tmp $to_actual || fail "Could not create worktree for $to"
cd "_worktree.tmp"
echo "Processing 'new'... (with output to screen)"
"$process" 2>&1 | tee /tmp/to.$$ || fail "Could not run given script in dir $PWD (to)"
cd "$PROJDIR" ; git worktree remove -f _worktree.tmp 2>/dev/null

# Process using previous version (from)
git worktree add -ff _worktree.tmp $from_actual || fail "Could not create worktree for $from"
cd "_worktree.tmp"
echo "Processing 'old'... (no output)"
"$process" >/tmp/from.$$ 2>&1 || echo "Could not run given script in dir $PWD (from).  Checking output anyway:"
cd "$PROJDIR" ; git worktree remove -f _worktree.tmp 2>/dev/null

echo "Comparing"
if ! cmp /tmp/{from,to}.$$ ; then
  echo "-----------------------------------------------------"
  echo "Difference found -> regression?  "
  echo "-----------------------------------------------------"
  echo "(From = $from, To = $to)"

  diff /tmp/{from,to}.$$
  echo "Side by side:"
  diff -y /tmp/{from,to}.$$
  echo "Keeping artifacts: from.output.txt and to.output.txt"
  (echo "Commit: $from_actual" >"$PROJDIR/from.output.txt" ; cat /tmp/from.$$ >>"$PROJDIR/from.output.txt")
  (echo "Commit: $to_actual" >"$PROJDIR/to.output.txt" ; cat /tmp/to.$$ >>"$PROJDIR/to.output.txt")
  cleanup
  exit 1
else
  echo "No difference"
  cleanup
  exit 0
fi
