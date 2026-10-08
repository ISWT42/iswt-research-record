#!/bin/bash
# Seal files: write <label>-SHA256.txt (sha256sum -b of the listed files), then ask FreeTSA for a time stamp of that file.
#   usage (from the folder that holds the files):  bash seal.sh <label> <file> [<file> ...]
#   makes:  <label>-SHA256.txt  <label>-SHA256.txt.tsq  <label>-SHA256.txt.tsr
# Only the hash file's SHA-256 leaves the PC (to freetsa.org); nothing else is sent. Refuses to overwrite.
set -u
label="$1"; shift
out="${label}-SHA256.txt"
if [ -e "$out" ] || [ -e "$out.tsq" ] || [ -e "$out.tsr" ]; then echo "refusing: $out (or its stamp) exists"; exit 1; fi
for f in "$@"; do [ -f "$f" ] || { echo "missing file: $f"; exit 1; }; done
sha256sum -b "$@" > "$out"
echo "sealed list:"; sed 's/^\(.\{12\}\)[0-9a-f]*/\1.../' "$out"
openssl ts -query -data "$out" -sha256 -no_nonce -cert -out "$out.tsq" 2>/dev/null || { echo "openssl query failed"; exit 1; }
for try in 1 2 3; do
  echo "clock before request: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  curl -s -m 60 -H "Content-Type: application/timestamp-query" --data-binary @"$out.tsq" https://freetsa.org/tsr -o "$out.tsr"
  echo "clock after reply:    $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  if openssl ts -reply -in "$out.tsr" -text 2>/dev/null | grep -q "Status: Granted"; then break; fi
  echo "no granted reply (try $try)"; rm -f "$out.tsr"; sleep 5
done
[ -f "$out.tsr" ] || { echo "FreeTSA gave no reply; the files are hashed but not stamped"; exit 2; }
python "$(dirname "$0")/seal_info.py" "$out"
