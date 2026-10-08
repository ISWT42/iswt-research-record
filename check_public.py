#!/usr/bin/env python3
"""check_public.py -- the done check for this public record.

Run from the repository root:   python check_public.py
It reads only files inside this folder. It exits 0 and prints "DONE CHECK: ALL PASS" when every line passes.

What it checks
  1  every file listed in every *-SHA256.txt / *.sha256 seal list is present and matches (so the seals verify);
     files left out on purpose are listed in WITHHELD.json with the hash the list gives them;
     entries that did not match even in the original folders are listed in SEAL-NOTES.json (checked exactly)
  2  no file name matches prediction / forecast patterns (seal artifacts of withheld forecast files are exempt and counted)
  3  zero hits in the published files for: the withheld idea's names, gmail, e-mail addresses other than the public
     contact address (and invented placeholder addresses), the word employer, AI Village record fields, the box's host
     and account names, a city name
  4  unsealed files carry no home path prefix; sealed files that do are counted (the user name alone is acceptable there)
  5  total size and file count per bundle
"""
import os, re, sys, json, hashlib, fnmatch

ROOT = os.path.dirname(os.path.abspath(__file__))
fails = 0
def out(ok, msg):
    global fails
    print(('PASS ' if ok else 'FAIL ') + msg)
    if not ok:
        fails += 1

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for ch in iter(lambda: f.read(1 << 20), b''):
            h.update(ch)
    return h.hexdigest()

def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, '/')

ALL = []
for r, ds, fs in os.walk(ROOT):
    ds[:] = [d for d in ds if d != '.git']
    for f in fs:
        ALL.append(os.path.join(r, f))
ALL.sort()

LIST_RX = re.compile(r'(-SHA256\.txt|\.sha256|SHA256SUMS|SHA256SUMS\.txt|MANIFEST-?[^/]*\.sha256)$', re.I)
SEAL_ART_RX = re.compile(r'(-SHA256\.txt|\.sha256|SHA256SUMS|\.tsr|\.tsq|\.ots|\.ots\.bak)$', re.I)
ENTRY_RX = re.compile(r'^([0-9a-fA-F]{64}) [ *](.+)$')

def load(name, default):
    p = os.path.join(ROOT, name)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else default

WITHHELD = load('WITHHELD.json', {'entries': []})
NOTES = load('SEAL-NOTES.json', {'known_mismatches': [], 'missing_at_source': [], 'directory_entries': []})
withheld_by_path = {}
for e in WITHHELD['entries']:
    withheld_by_path[e['path']] = e
withheld_by_sha = {}
for e in WITHHELD['entries']:
    if e.get('sha256'):
        withheld_by_sha[e['sha256']] = e
known_mm = {(m['list'], m['entry']): m for m in NOTES['known_mismatches']}
BYBASE = {}
for _p in ALL:
    BYBASE.setdefault(os.path.basename(_p), []).append(_p)
missing_src = {(m['list'], m['entry']) for m in NOTES['missing_at_source']}

def evaluate():
    """Returns dict of counters and problem lists for all seal lists in the repo."""
    res = dict(lists=0, entries=0, ok=0, withheld_ok=0, known_mismatch=0, missing_src=0, stdin=0, dirs=0, empty_lists=0, problems=[], mismatches=[], unlisted_missing=[], mismatch_detail=[], missing_detail=[])
    for p in ALL:
        if not LIST_RX.search(os.path.basename(p)):
            continue
        try:
            lines = open(p, encoding='utf-8', errors='replace').read().split('\n')
        except Exception:
            continue
        ents = [ENTRY_RX.match(l.rstrip('\r')) for l in lines]
        ents = [m for m in ents if m]
        if not ents:
            res['empty_lists'] += 1
            continue
        res['lists'] += 1
        base = os.path.dirname(p)
        for m in ents:
            h, rp = m.group(1).lower(), m.group(2).strip()
            res['entries'] += 1
            if rp == '-':
                res['stdin'] += 1
                continue
            rpn = rp.replace('\\', '/')
            while rpn.startswith('./'):
                rpn = rpn[2:]
            target = os.path.normpath(os.path.join(base, rpn.replace('/', os.sep)))
            key = (rel(p), re.sub('joshd', '<user>', rp, flags=re.I))
            if not os.path.exists(target):
                # some lists name files relative to a sub-folder of their own folder: look for a unique file with that tail
                tail = os.sep + rpn.replace('/', os.sep)
                cands = [c for c in BYBASE.get(os.path.basename(rpn), []) if c.startswith(base + os.sep) and (c.endswith(tail) or c == os.path.join(base, rpn))]
                if len(cands) > 1:
                    cands = [c for c in cands if sha256_file(c) == h] or cands[:1]
                if cands:
                    target = cands[0]
            if os.path.isfile(target):
                a = sha256_file(target)
                if a == h:
                    res['ok'] += 1
                elif key in known_mm and known_mm[key]['actual'] == a and known_mm[key]['listed'] == h:
                    res['known_mismatch'] += 1
                else:
                    res['problems'].append('MISMATCH %s -> %s' % (rel(p), rp))
                    res['mismatches'].append(key)
                    res['mismatch_detail'].append({'list': rel(p), 'entry': key[1], 'listed': h, 'actual': a})
            elif os.path.isdir(target):
                res['dirs'] += 1
            else:
                tr = rel(target)
                w = withheld_by_path.get(tr)
                if w is None:
                    w = withheld_by_sha.get(h)
                if w is not None and (w.get('sha256') in (None, h)):
                    res['withheld_ok'] += 1
                elif key in missing_src:
                    res['missing_src'] += 1
                else:
                    res['problems'].append('MISSING %s -> %s' % (rel(p), rp))
                    res['unlisted_missing'].append(key)
                    res['missing_detail'].append({'list': rel(p), 'entry': key[1], 'listed': h, 'path': tr})
    return res

def main():
    # ---------------------------------------------------------------- 1 seals
    res = evaluate()
    out(not res['problems'],
        '1. seal lists %d, entries %d: %d match; %d are files left out on purpose (hash recorded in WITHHELD.json); %d did not match in the original folders either (SEAL-NOTES.json); '
        '%d not in the original folders; %d folder entries; %d stdin entries; problems %d' % (
            res['lists'], res['entries'], res['ok'], res['withheld_ok'], res['known_mismatch'], res['missing_src'], res['dirs'], res['stdin'], len(res['problems'])))
    for pr in res['problems'][:15]:
        print('     ', pr)
    out(res['ok'] > 0 and res['lists'] > 0, '   at least one seal list was checked: %d lists, %d entries verified' % (res['lists'], res['ok']))
    # redacted copies and their originals
    red = [p for p in ALL if '.redacted.' in os.path.basename(p)]
    bad = []
    for p in red:
        orig = rel(p).replace('.redacted.', '.', 1)
        w = withheld_by_path.get(orig)
        if not w or w.get('replaced_by') is None or not w.get('sha256'):
            bad.append(rel(p))
    out(not bad, '   redacted copies %d, each has its withheld original and hash recorded: %d without' % (len(red), len(bad)))
    # ---------------------------------------------------------------- 2 names
    name_rx = re.compile(r'predict|forecast', re.I)
    bad_names, exempt = [], []
    for p in ALL:
        b = os.path.basename(p)
        if name_rx.search(b):
            (exempt if SEAL_ART_RX.search(b) else bad_names).append(rel(p))
    out(not bad_names, '2. files whose names match prediction/forecast patterns: %d %s (seal artifacts of withheld forecast files, kept so the seal chain verifies: %d)' % (len(bad_names), bad_names[:5], len(exempt)))
    # ---------------------------------------------------------------- 3 content
    frag = [('stab' + 'le', '[- _]?var' + 'iables?'), ('sav' + 'ed', '[- _]var' + 'iables?'), ('F' + 'C', '-' + '4')]
    idea_rx = re.compile(frag[0][0] + frag[0][1] + '|' + frag[1][0] + frag[1][1] + '|(?<![A-Za-z0-9_+/=-])' + frag[2][0] + frag[2][1] + '(?![A-Za-z0-9])', re.I)
    gmail_rx = re.compile(r'@gmail|gmail\.com', re.I)
    employer_rx = re.compile(r'employer', re.I)
    city_rx = re.compile(r'\b' + 'otta' + 'wa' + r'\b', re.I)
    aiv_rx = re.compile(r'"(agent_speaker_id|speaker_type|room_id|agent_messages|session_goal|agent_display_name)"\s*:', re.I)
    box_rx = re.compile('|'.join(['sonny' + 'side', 'rra' + 'gent', 'day' + 'break' + 'agent', 'ms' + 'home' + r'\.net', 'hyper-' + 'v', 'tail' + 'scale', r'\.ts\.net', 'iswt42@iswt42']), re.I)
    email_rx = re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+')
    port_rx = re.compile(r'(?:localhost|127\.0\.0\.1):\d{2,5}')
    jev_rx = re.compile(r'\bJev\b')
    home_rx = re.compile(r'joshd', re.I)
    ok_full = {'joshua@iswt.ca', 'busilezas@mailbox.org'}
    synth = {'example.com', 'example.org', 'example.net', 'vendor.com', 'company.com', 'trothgrud.app', 'github.com', '2x.jpg', 'v22.18.0'}
    def email_ok(e):
        d = e.split('@', 1)[1].lower()
        if e.lower() in ok_full or re.fullmatch(r'[\d.]+', d):
            return True
        if d.endswith(('.example', '.invalid', '.internal', '.lab', '.local', '.test', '.localhost', '.example.com', '.example.org', '.example.net')):
            return True
        return d in synth
    cnt = {k: [] for k in ('idea', 'gmail', 'email', 'employer', 'city', 'aiv', 'box')}
    ports, jev, covered_home, uncovered_home = [], [], [], []
    # covered = listed in some seal list, or has a seal companion
    listed = set()
    for p in ALL:
        if LIST_RX.search(os.path.basename(p)):
            try:
                for l in open(p, encoding='utf-8', errors='replace').read().split('\n'):
                    m = ENTRY_RX.match(l.rstrip('\r'))
                    if m and m.group(2).strip() != '-':
                        t = os.path.normpath(os.path.join(os.path.dirname(p), m.group(2).strip().replace('\\', '/').lstrip('./').replace('/', os.sep)))
                        listed.add(t)
            except Exception:
                pass
    tokens = set()
    HEX = re.compile(r'(?<![0-9a-fA-F])[0-9a-f]{64}(?![0-9a-fA-F])')
    for q in ALL:
        if q.lower().endswith(('.tsr', '.tsq', '.ots', '.bak')) or os.path.getsize(q) > 3000000:
            continue
        try:
            tokens.update(HEX.findall(open(q, encoding='utf-8').read()))
        except Exception:
            pass
    def covered(p):
        if SEAL_ART_RX.search(os.path.basename(p)) or p in listed:
            return True
        try:
            if sha256_file(p) in tokens:
                return True
        except Exception:
            pass
        return any(os.path.exists(p + e) for e in ('.tsr', '.tsq', '.ots')) or any(os.path.exists(os.path.splitext(p)[0] + e) for e in ('.tsr', '.tsq'))
    scanned = 0
    for p in ALL:
        b = os.path.basename(p)
        if b.lower().endswith(('.tsr', '.tsq', '.ots', '.bak')) or p.startswith(os.path.join(ROOT, 'check_public.py')):
            continue
        if b == 'check_public.py':
            continue
        try:
            t = open(p, encoding='utf-8').read()
        except Exception:
            continue
        scanned += 1
        r_ = rel(p)
        if idea_rx.search(t): cnt['idea'].append(r_)
        if gmail_rx.search(t): cnt['gmail'].append(r_)
        if employer_rx.search(t): cnt['employer'].append(r_)
        if city_rx.search(t): cnt['city'].append(r_)
        if aiv_rx.search(t): cnt['aiv'].append(r_)
        if box_rx.search(t): cnt['box'].append(r_)
        for m in email_rx.finditer(t):
            if not email_ok(m.group(0)):
                cnt['email'].append(r_ + ' ' + m.group(0)); break
        if port_rx.search(t): ports.append(r_)
        if jev_rx.search(t): jev.append(r_)
        n = len(home_rx.findall(t))
        if n:
            (covered_home if covered(p) else uncovered_home).append((r_, n))
    out(True, '   text files scanned: %d' % scanned)
    out(not cnt['idea'], '3. withheld-idea patterns: %d hits %s' % (len(cnt['idea']), cnt['idea'][:3]))
    out(not cnt['gmail'], '   "gmail": %d hits %s' % (len(cnt['gmail']), cnt['gmail'][:3]))
    out(not cnt['email'], '   e-mail addresses other than the public contact address and invented placeholders: %d hits %s' % (len(cnt['email']), cnt['email'][:3]))
    out(not cnt['employer'], '   "employer": %d hits %s' % (len(cnt['employer']), cnt['employer'][:3]))
    out(not cnt['city'], '   city name of residence: %d hits %s' % (len(cnt['city']), cnt['city'][:3]))
    out(not cnt['aiv'], '   AI Village record fields: %d hits %s' % (len(cnt['aiv']), cnt['aiv'][:3]))
    out(not cnt['box'], '   box host and account names: %d hits %s' % (len(cnt['box']), cnt['box'][:3]))
    print('INFO  local-server ports written as localhost:NNNN or 127.0.0.1:NNNN (PC-local model servers and demos, not the box): %d files %s' % (len(ports), ports[:4]))
    print('INFO  the word Jev (the decision-model persona) in non-data files: %d files %s' % (len(jev), jev[:4]))
    # ---------------------------------------------------------------- 4 paths
    out(not uncovered_home, '4. files not covered by a seal that still contain the user name in a path: %d %s' % (len(uncovered_home), uncovered_home[:3]))
    print('INFO  sealed files that contain the user name "joshd" (left unchanged; user name alone): %d files, %d occurrences' % (len(covered_home), sum(n for _, n in covered_home)))
    # ---------------------------------------------------------------- 5 size
    total = sum(os.path.getsize(p) for p in ALL)
    out(True, '5. total size %.1f MB in %d files' % (total / 1e6, len(ALL)))
    bundles = {}
    for p in ALL:
        top = rel(p).split('/')[0]
        b = bundles.setdefault(top, [0, 0])
        b[0] += 1; b[1] += os.path.getsize(p)
    for k in sorted(bundles):
        if re.match(r'\d-', k):
            print('      %-48s %5d files %8.2f MB' % (k, bundles[k][0], bundles[k][1] / 1e6))
    print('DONE CHECK:', 'ALL PASS' if fails == 0 else '%d FAIL' % fails)
    return 1 if fails else 0

if __name__ == '__main__':
    sys.exit(main())
