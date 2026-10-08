// Reads the COMMAND of a tool call (never its output) to say what kind of operation it was:
//   families  which operations it ran: test, build, push, merge, commit, http, deploy, send, create, install
//   isRead    true when every command in it only reads or echoes (cat, grep, ls, git status, kubectl get ...). A read
//             can never settle a claim that something was done, and an echo is how an agent could print its own "receipt".
//   isEcho    some command in it prints text (echo, printf, Write-Host)
//   http      for curl and friends: {method, url, bareStatus}
//
// Heuristic by design. A command it cannot classify is an ordinary operation with no family, so no rule treats
// its output as a test report or a push result, and the claim stays "not shown".

const WRAPPERS = new Set(['sudo', 'time', 'command', 'builtin', 'exec', 'nohup', 'winpty', 'call', 'npx', 'bunx', 'pnpx', 'doas', 'xargs']);
const NEUTRAL = new Set(['cd', 'pushd', 'popd', 'export', 'set', 'unset', 'source', '.', 'sleep', 'wait', 'true', 'false', 'pwd', ':', 'clear', 'cls', 'exit', 'return', 'trap', 'shopt', 'umask', 'ulimit', 'alias', 'set-location', 'sl', 'set-strictmode']);
const ECHO_PROGS = new Set(['echo', 'printf', 'write-host', 'write-output', 'write-verbose', 'write-information', 'print']);
const READ_PROGS = new Set(['cat', 'type', 'head', 'tail', 'less', 'more', 'grep', 'egrep', 'fgrep', 'rg', 'ag', 'ack', 'ls', 'dir', 'll', 'find', 'stat', 'wc',
  'diff', 'cmp', 'which', 'where', 'whoami', 'hostname', 'test', '[', '[[', 'date', 'uname', 'env', 'printenv', 'id', 'file', 'tree', 'du', 'df', 'ps', 'top',
  'jq', 'sort', 'uniq', 'cut', 'tr', 'awk', 'sed', 'basename', 'dirname', 'realpath', 'readlink', 'md5sum', 'sha256sum', 'sha1sum', 'shasum', 'xxd', 'od',
  'get-content', 'gc', 'get-childitem', 'gci', 'get-item', 'get-process', 'select-string', 'sls', 'test-path', 'measure-object', 'convertfrom-json', 'convertto-json',
  'format-table', 'format-list', 'out-string', 'select-object', 'where-object', 'sort-object', 'get-date', 'get-location', 'get-command', 'resolve-path', 'get-filehash',
  'node-version', 'python-version', 'column', 'nl', 'rev', 'tac', 'yes', 'seq', 'expr', 'bc', 'lsof', 'netstat', 'ss', 'nslookup', 'dig', 'ping', 'tracert', 'traceroute',
  'history', 'man', 'help', 'whereis', 'type']);
const GIT_READ = new Set(['status', 'log', 'diff', 'show', 'ls-remote', 'rev-parse', 'rev-list', 'blame', 'describe', 'reflog', 'shortlog', 'grep', 'ls-files',
  'ls-tree', 'cat-file', 'show-ref', 'name-rev', 'merge-base', 'diff-tree', 'for-each-ref', 'whatchanged', 'help', 'version', 'fetch', 'count-objects',
  'check-ignore', 'cherry', 'range-diff', 'verify-commit', 'verify-tag', 'archive', 'bundle']);
const GIT_VALUE_OPTS = new Set(['-C', '-c', '--git-dir', '--work-tree', '--namespace', '--exec-path', '--super-prefix']);
const KUBECTL_READ = new Set(['get', 'describe', 'logs', 'top', 'version', 'config', 'explain', 'api-resources', 'api-versions', 'cluster-info', 'auth', 'diff', 'events', 'wait']);
const KUBECTL_VERBS = new Set([...KUBECTL_READ, 'rollout', 'apply', 'create', 'delete', 'patch', 'set', 'scale', 'expose', 'run', 'exec', 'cp', 'label', 'annotate', 'taint', 'drain', 'cordon', 'uncordon', 'edit', 'replace', 'autoscale', 'port-forward', 'proxy', 'attach', 'debug', 'kustomize']);
const DOCKER_READ = new Set(['ps', 'images', 'inspect', 'logs', 'version', 'info', 'history', 'stats', 'top', 'port', 'diff', 'search', 'ls', 'list']);
const NPM_READ = new Set(['view', 'info', 'ls', 'list', 'outdated', 'whoami', 'ping', 'help', 'explain', 'search', 'root', 'prefix', 'bin', 'config', 'audit', 'doctor', 'fund', 'pack']);
const PIP_READ = new Set(['list', 'show', 'freeze', 'check', 'config', 'download', 'help', 'inspect', 'index']);
const TERRAFORM_READ = new Set(['plan', 'show', 'validate', 'fmt', 'output', 'version', 'providers', 'graph', 'state', 'workspace', 'init']);
const GH_READ = new Set(['view', 'list', 'status', 'checks', 'diff', 'watch', 'download', 'browse']);

// ---- splitting a command line into commands ---------------------------------------------------------------
function stripHeredocs(command) {
  const lines = String(command ?? '').split('\n');
  const kept = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    kept.push(line);
    const markers = [...line.matchAll(/<<-?\s*(['"]?)([A-Za-z_][\w]*)\1/g)].map((m) => m[2]);
    const hereString = /@['"]\s*$/.test(line) ? [line.trimEnd().endsWith("@'") ? "'@" : '"@'] : [];
    for (const marker of [...markers, ...hereString]) {
      let j = i + 1;
      while (j < lines.length && lines[j].trim() !== marker) j++;
      if (j < lines.length) i = j; // skip the body and its terminator
      else break;
    }
  }
  return kept.join('\n');
}

export function splitSegments(command, { powershell = false } = {}) {
  const s = stripHeredocs(command);
  const segments = [];
  let current = '';
  let quote = null;
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (quote) {
      current += c;
      if (c === '\\' && quote === '"' && !powershell && i + 1 < s.length) { current += s[++i]; continue; }
      if (c === quote) quote = null;
      continue;
    }
    if (powershell && c === '`') { current += c + (s[i + 1] ?? ''); i++; continue; }
    if (c === '"' || c === "'" || (!powershell && c === '`')) { quote = c; current += c; continue; }
    if (c === '\n' || c === ';') { segments.push(current); current = ''; continue; }
    if (c === '|') { segments.push(current); current = ''; if (s[i + 1] === '|') i++; continue; }
    if (c === '&') {
      const prev = s[i - 1];
      const next = s[i + 1];
      if (prev === '>' || prev === '<' || next === '>') { current += c; continue; } // 2>&1, &>
      segments.push(current); current = '';
      if (next === '&') i++;
      continue;
    }
    current += c;
  }
  segments.push(current);
  return segments.map((x) => x.trim()).filter(Boolean);
}

export function tokenize(segment) {
  const tokens = [];
  let current = '';
  let quote = null;
  let started = false;
  for (let i = 0; i < segment.length; i++) {
    const c = segment[i];
    if (quote) {
      if (c === '\\' && quote === '"' && segment[i + 1] === '"') { current += '"'; i++; continue; }
      if (c === quote) { quote = null; continue; }
      current += c;
      continue;
    }
    if (c === '"' || c === "'") { quote = c; started = true; continue; }
    if (/\s/.test(c)) { if (started || current) { tokens.push(current); current = ''; started = false; } continue; }
    current += c;
    started = true;
  }
  if (started || current) tokens.push(current);
  return tokens;
}

const baseName = (token) => String(token).replace(/\\/g, '/').split('/').pop().toLowerCase().replace(/\.(?:exe|cmd|bat|com)$/, '');

// Drop a leading wrapper (sudo, npx, env VAR=x, timeout 30, ...) and variable assignments.
function stripWrappers(tokens) {
  const t = [...tokens];
  for (let guard = 0; guard < 8 && t.length > 0; guard++) {
    t[0] = t[0].replace(/^[({!]+/, '');
    if (t[0] === '') { t.shift(); continue; }
    if (/^[A-Za-z_][A-Za-z0-9_]*=/.test(t[0])) { t.shift(); continue; }
    const head = baseName(t[0]);
    if (WRAPPERS.has(head)) { t.shift(); while (t[0] && t[0].startsWith('-') && head !== 'xargs') t.shift(); continue; }
    if (head === 'env') { t.shift(); while (t[0] && (t[0].startsWith('-') || /^[A-Za-z_][A-Za-z0-9_]*=/.test(t[0]))) t.shift(); continue; }
    if (head === 'timeout' || head === 'nice') { t.shift(); while (t[0] && (t[0].startsWith('-') || /^[\d.]+[smhd]?$/.test(t[0]))) t.shift(); continue; }
    if ((head === 'uv' || head === 'poetry' || head === 'pipenv') && t[1] === 'run') { t.splice(0, 2); continue; }
    if ((head === 'pnpm' || head === 'yarn') && t[1] === 'dlx') { t.splice(0, 2); continue; }
    break;
  }
  return t;
}

const SHELL_C = /^(?:bash|sh|zsh|dash|ksh|pwsh|powershell|cmd)$/;

// A dry run prints what it WOULD do, often in the very lines a real run prints ("4f1c2aa..9b3e771  main -> main"), and
// changes nothing. It is preparation, never a receipt.
const DRY_FLAG = /^--?(?:dry[-_]?run|simulate|what-?if|noop|no-op|plan-only|no-execute-changeset)(?:=.*)?$/i;
const SHORT_N = /^-[A-Za-z]*n[A-Za-z]*$/;
function isDryRun(prog, args, rawTokens) {
  if (rawTokens.some((t) => /^DRY_?RUN=(?:1|true|yes|on)$/i.test(t))) return true;
  if (args.some((a) => DRY_FLAG.test(a))) return true;
  if (prog === 'git' && args.includes('push') && args.some((a) => SHORT_N.test(a))) return true;          // git push -n
  if (prog === 'rsync' && args.some((a) => SHORT_N.test(a))) return true;                                  // rsync -avn
  if ((prog === 'make' || prog === 'gmake') && args.some((a) => /^(?:-n|--just-print|--recon)$/.test(a))) return true;
  if (prog === 'ansible-playbook' && args.some((a) => /^(?:--check|-C)$/.test(a))) return true;
  return false;
}

// ---- classifying one command -----------------------------------------------------------------------------
function npmScript(args) {
  // npm/yarn/pnpm/bun: the script run: "test", "run test", "run build", "build" (yarn)
  const rest = args.filter((a) => !a.startsWith('-'));
  if (rest[0] === 'run' || rest[0] === 'run-script') return rest[1] ?? '';
  return rest[0] ?? '';
}

function classifyJs(prog, args, out) {
  const script = npmScript(args);
  if (/^(?:install|i|add|ci|update|upgrade)$/.test(script) || (prog !== 'npm' && script === '' && args.length === 0)) out.families.add('install');
  if (/^(?:test|t|tests|test:.*|check|ci:test|unit|e2e|spec|coverage|jest|vitest|mocha)$/.test(script)) out.families.add('test');
  if (/^(?:build|compile|lint|lint:.*|typecheck|type-check|types|check-types|tsc|format:check|prettier:check|build:.*)$/.test(script)) out.families.add('build');
  if (/^(?:publish|deploy|release|ship|deploy:.*|release:.*|publish:.*)$/.test(script)) out.families.add('deploy');
  if (prog === 'bun' && args[0] === 'test') out.families.add('test');
  if (prog === 'npm' || prog === 'yarn' || prog === 'pnpm') {
    if (NPM_READ.has(script) && !out.families.size) out.read = true;
  }
}

function classifyCommand(rawTokens) {
  const tokens = stripWrappers(rawTokens);
  const out = { prog: '', sub: '', families: new Set(), read: false, echo: false, neutral: false, http: null, inner: null, tokens };
  if (tokens.length === 0) { out.neutral = true; return out; }
  const prog = baseName(tokens[0]);
  const args = tokens.slice(1);
  out.prog = prog;

  if (NEUTRAL.has(prog)) { out.neutral = true; return out; }
  if (ECHO_PROGS.has(prog)) { out.echo = true; out.read = true; return out; }

  // bash -c "...", pwsh -Command "...", cmd /c "..."
  if (SHELL_C.test(prog)) {
    const flag = args.findIndex((a) => /^(?:-c|-lc|-command|-c|\/c|\/k|-encodedcommand)$/i.test(a));
    if (flag >= 0 && args[flag + 1]) { out.inner = args.slice(flag + 1).join(' '); return out; }
  }

  // keep what the command is (so a card can say "only a dry run"), but it is a read: it cannot settle anything
  if (isDryRun(prog, args, rawTokens)) out.dry = true;

  switch (prog) {
    case 'git': {
      let sub = '';
      for (let i = 0; i < args.length; i++) {
        const a = args[i];
        if (GIT_VALUE_OPTS.has(a)) { i++; continue; }
        if (a.startsWith('-')) continue;
        sub = a;
        break;
      }
      out.sub = sub;
      if (sub === 'push') out.families.add('push');
      else if (sub === 'merge') out.families.add('merge');
      else if (sub === 'pull') { out.families.add('merge'); }
      else if (sub === 'commit') out.families.add('commit');
      else if (sub === 'tag' && (args.filter((a) => !a.startsWith('-')).length <= 1 || args.some((a) => /^(?:-l|--list)$/.test(a)))) out.read = true;
      else if (sub === 'branch' && !args.some((a) => /^-(?:d|D|m|M|c|C|-delete|-move|-copy)$/.test(a)) && args.filter((a) => !a.startsWith('-')).length <= 1) out.read = true;
      else if (sub === 'remote' && !args.some((a) => /^(?:add|remove|rm|rename|set-url|set-head|prune)$/.test(a))) out.read = true;
      else if (sub === 'config' && !args.some((a) => /^--(?:add|unset|replace-all|edit)/.test(a)) && args.filter((a) => !a.startsWith('-')).length <= 2) out.read = true;
      else if (sub === 'stash' && /^(?:list|show)$/.test(args[args.indexOf('stash') + 1] ?? args.find((a) => /^(?:list|show)$/.test(a)) ?? '')) out.read = true;
      else if (GIT_READ.has(sub)) out.read = true;
      return out;
    }
    case 'gh': {
      const [a, b] = args.filter((x) => !x.startsWith('-'));
      out.sub = [a, b].filter(Boolean).join(' ');
      if (a === 'pr' && b === 'merge') out.families.add('merge');
      else if ((a === 'pr' || a === 'issue') && b === 'create') { out.families.add('create'); out.families.add('send'); }
      else if (a === 'release' && b === 'create') { out.families.add('create'); out.families.add('deploy'); }
      else if ((a === 'pr' || a === 'issue') && /^(?:comment|review)$/.test(b ?? '')) out.families.add('send');
      else if (a === 'api') {
        out.families.add('http');
        const mi = args.findIndex((x) => /^(?:-X|--method)$/.test(x));
        const mEq = args.find((x) => /^--method=/.test(x));
        let method = mi >= 0 ? args[mi + 1] : mEq ? mEq.split('=')[1] : null;
        if (!method && args.some((x) => /^(?:-f|-F|--field|--raw-field|--input)$/.test(x))) method = 'POST';
        out.http = { method: (method ?? 'GET').toUpperCase(), url: args.find((x) => /^\/?[\w-]+\//.test(x) && !x.startsWith('-')) ?? '', bareStatus: false };
      } else if (a === 'workflow' && b === 'run') out.families.add('deploy');
      else if (GH_READ.has(b ?? '') || /^(?:auth|config|search|repo)$/.test(a ?? '') && /^(?:status|view|list)$/.test(b ?? '')) out.read = true;
      return out;
    }
    case 'curl': case 'wget': case 'http': case 'https': case 'xh': case 'invoke-restmethod': case 'irm': case 'invoke-webrequest': case 'iwr': {
      out.families.add('http');
      out.http = httpOf(prog, args);
      return out;
    }
    case 'kubectl': case 'oc': {
      const sub = args.find((x) => KUBECTL_VERBS.has(x)) ?? '';
      out.sub = sub;
      if (sub === 'rollout') { out.families.add('deploy'); out.read = args.includes('status') || args.includes('history'); }
      else if (KUBECTL_READ.has(sub)) out.read = true;
      else out.families.add('deploy');
      return out;
    }
    case 'docker': case 'podman': {
      const sub = args.find((a) => !a.startsWith('-')) ?? '';
      out.sub = sub;
      if (sub === 'push') out.families.add('deploy');
      else if (sub === 'build' || sub === 'buildx') out.families.add('build');
      else if (DOCKER_READ.has(sub)) out.read = true;
      return out;
    }
    case 'helm': case 'terraform': case 'tofu': case 'pulumi': case 'serverless': case 'sls': case 'cdk': case 'vercel': case 'netlify': case 'wrangler':
    case 'flyctl': case 'fly': case 'firebase': case 'heroku': case 'eb': case 'gcloud': case 'az': case 'aws': case 'sam': case 'ansible-playbook': {
      const sub = args.find((a) => !a.startsWith('-')) ?? '';
      out.sub = sub;
      if ((prog === 'terraform' || prog === 'tofu') && TERRAFORM_READ.has(sub)) { out.read = true; return out; }
      if (/^(?:get|list|describe|show|status|whoami|version|logs|history|help|ls|info|diff|plan|preview)$/.test(sub) && !args.some((a) => /^(?:deploy|apply|publish|release|update|create|put|sync|rollback)$/.test(a))) { out.read = true; return out; }
      out.families.add('deploy');
      return out;
    }
    case 'npm': case 'yarn': case 'pnpm': case 'bun': {
      const script = npmScript(args);
      if (script === 'publish' || script === 'deploy' || script === 'release') out.families.add('deploy');
      classifyJs(prog, args, out);
      if (prog === 'npm' && script === 'publish') out.families.add('deploy');
      return out;
    }
    case 'pip': case 'pip3': case 'pipx': case 'uv': case 'conda': case 'mamba': {
      const sub = args.find((a) => !a.startsWith('-')) ?? '';
      if (/^(?:install|add|sync)$/.test(sub) || (prog === 'uv' && sub === 'pip' && args.includes('install'))) out.families.add('install');
      else if (PIP_READ.has(sub)) out.read = true;
      return out;
    }
    case 'python': case 'python3': case 'py': {
      const mi = args.indexOf('-m');
      const mod = mi >= 0 ? (args[mi + 1] ?? '') : '';
      if (/^(?:pytest|unittest|nose2?|tox)$/.test(mod)) out.families.add('test');
      else if (mod === 'pip' && args.includes('install')) out.families.add('install');
      else if (mod === 'pip' && PIP_READ.has(args[mi + 2] ?? '')) out.read = true;
      else if (/^(?:mypy|ruff|flake8|pylint|pyright|black|build|compileall|py_compile)$/.test(mod)) out.families.add('build');
      else if (mod === 'http.server' || mod === 'json.tool') out.read = true;
      const script = args.find((a) => !a.startsWith('-') && /\.py$/i.test(a));
      if (script && /(?:^|[/\\_.-])tests?(?:[/\\_.-]|$)/i.test(script)) out.families.add('test');
      if (args.includes('-c') && /\brequests\.(get|post|put|patch|delete)\b|urllib|http\.client|urlopen|httpx\./.test(args.join(' '))) out.families.add('http');
      return out;
    }
    case 'pytest': case 'py.test': case 'tox': case 'nox': case 'jest': case 'vitest': case 'mocha': case 'ava': case 'tap': case 'rspec': case 'phpunit': case 'pest':
    case 'ctest': case 'bats': case 'nextest': case 'cypress': case 'playwright': case 'karma': case 'jasmine': case 'behave': case 'robot': case 'unittest':
      out.families.add('test');
      return out;
    case 'node': case 'deno': {
      if (args.some((a) => /^--test(?:$|=|-)/.test(a)) || (prog === 'deno' && args[0] === 'test')) out.families.add('test');
      const script = args.find((a) => !a.startsWith('-') && /\.(?:m?js|cjs|ts)$/i.test(a));
      if (script && /(?:^|[/\\_.-])tests?(?:[/\\_.-]|$)/i.test(script)) out.families.add('test');
      if (args.includes('-e') && /\bfetch\(|https?\.request|axios|got\(/.test(args.join(' '))) out.families.add('http');
      return out;
    }
    case 'go': {
      const sub = args.find((a) => !a.startsWith('-')) ?? '';
      if (sub === 'test') out.families.add('test');
      else if (sub === 'build' || sub === 'vet') out.families.add('build');
      else if (sub === 'install' || sub === 'get') out.families.add('install');
      else if (/^(?:list|env|version|doc|help)$/.test(sub)) out.read = true;
      return out;
    }
    case 'cargo': {
      const sub = args.find((a) => !a.startsWith('-') && !a.startsWith('+')) ?? '';
      if (sub === 'test' || sub === 'nextest' || sub === 'bench') out.families.add('test');
      else if (/^(?:build|check|clippy|fmt|doc)$/.test(sub)) out.families.add('build');
      else if (sub === 'publish') out.families.add('deploy');
      else if (/^(?:install|add)$/.test(sub)) out.families.add('install');
      else if (/^(?:tree|search|metadata|version|help)$/.test(sub)) out.read = true;
      return out;
    }
    case 'mvn': case 'mvnw': case './mvnw': case 'gradle': case 'gradlew': case 'sbt': case 'ant': {
      const goals = args.filter((a) => !a.startsWith('-')).join(' ');
      if (/\b(?:test|verify|integration-test|check|build|install|package)\b/.test(goals)) out.families.add('test');
      if (/\b(?:compile|build|package|install|assemble|jar|war)\b/.test(goals)) out.families.add('build');
      if (/\b(?:deploy|publish)\b/.test(goals)) out.families.add('deploy');
      return out;
    }
    case 'dotnet': {
      const sub = args.find((a) => !a.startsWith('-')) ?? '';
      if (sub === 'test') out.families.add('test');
      else if (/^(?:build|publish|pack|restore|msbuild)$/.test(sub)) { out.families.add('build'); if (sub === 'publish') out.families.add('deploy'); }
      return out;
    }
    case 'make': case 'gmake': case 'nmake': case 'ninja': case 'cmake': case 'msbuild': case 'rake': {
      const target = args.filter((a) => !a.startsWith('-')).join(' ');
      if (/\b(?:test|tests|check|spec)\b/.test(target)) out.families.add('test');
      else if (/\b(?:deploy|release|publish|ship)\b/.test(target)) out.families.add('deploy');
      else out.families.add('build');
      return out;
    }
    case 'tsc': case 'eslint': case 'ruff': case 'mypy': case 'pyright': case 'flake8': case 'pylint': case 'clippy-driver': case 'biome': case 'prettier':
    case 'webpack': case 'vite': case 'rollup': case 'esbuild': case 'parcel': case 'next': case 'gcc': case 'g++': case 'clang': case 'rustc': case 'javac': case 'black':
      out.families.add('build');
      return out;
    case 'twine': case 'flit': case 'poetry': {
      if (/^(?:upload|publish)$/.test(args[0] ?? '')) out.families.add('deploy');
      else if (prog === 'poetry' && /^(?:install|add)$/.test(args[0] ?? '')) out.families.add('install');
      return out;
    }
    case 'apt': case 'apt-get': case 'brew': case 'winget': case 'choco': case 'scoop': case 'gem': case 'composer': case 'dnf': case 'yum': case 'pacman': case 'apk':
      if (args.some((a) => /^(?:install|add|require|upgrade)$/.test(a))) out.families.add('install');
      return out;
    case 'mail': case 'sendmail': case 'mutt': case 'msmtp': case 'swaks': case 'ssmtp': case 'send-mailmessage': case 'slack': case 'slack-cli':
      out.families.add('send');
      return out;
    default:
      break;
  }

  if (ECHO_PROGS.has(prog)) { out.echo = true; out.read = true; return out; }
  if (READ_PROGS.has(prog)) {
    out.read = true;
    // sed -i and tee write files; find -delete / -exec act
    if ((prog === 'sed' && args.some((a) => /^-[a-z]*i/.test(a))) || (prog === 'find' && args.some((a) => /^-(?:delete|exec|execdir)$/.test(a)))) out.read = false;
    return out;
  }
  // a script whose name says what it does
  const script = tokens.find((t, i) => i <= 2 && /(?:^|[/\\])[\w.-]+\.(?:sh|bash|ps1|py|js|mjs|ts|rb|pl|cmd|bat)$/i.test(t)) ?? (prog.startsWith('.') ? prog : '');
  if (script) {
    if (/(?:^|[/\\_.-])tests?(?:[/\\_.-]|\.|$)/i.test(script)) out.families.add('test');
    if (/(?:^|[/\\_.-])(?:deploy|release|publish|ship)(?:[/\\_.-]|\.|$)/i.test(script)) out.families.add('deploy');
    if (/(?:^|[/\\_.-])build(?:[/\\_.-]|\.|$)/i.test(script)) out.families.add('build');
    if (/(?:^|[/\\_.-])(?:send|mail|notify)(?:[/\\_.-]|\.|$)/i.test(script)) out.families.add('send');
  }
  return out;
}

function httpOf(prog, args) {
  let method = null;
  let url = '';
  let bareStatus = false;
  let data = false;
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    const next = args[i + 1];
    if (/^(?:-X|--request|-method|-Method)$/i.test(a) && next) { method = next.toUpperCase(); i++; continue; }
    if (/^--request=|^--method=/i.test(a)) { method = a.split('=')[1].toUpperCase(); continue; }
    if (/^(?:-d|--data|--data-raw|--data-binary|--data-urlencode|-F|--form|--json|-T|--upload-file|--post-data|--post-file|-Body|-InFile)(?:=|$)/i.test(a)) data = true;
    if (/^(?:-I|--head)$/.test(a)) method = method ?? 'HEAD';
    if (/^(?:-w|--write-out)$/.test(a) && /http_code/.test(next ?? '')) bareStatus = true;
    if (/^--write-out=.*http_code/.test(a)) bareStatus = true;
    if (/^(?:-uri|-Uri)$/i.test(a) && next) { url = next; i++; continue; }
    if (!url && /^https?:\/\//i.test(a)) url = a;
    if (prog === 'http' || prog === 'https' || prog === 'xh') {
      if (/^(?:GET|POST|PUT|PATCH|DELETE|HEAD)$/i.test(a) && !method) method = a.toUpperCase();
      if (/^[\w.-]+=/.test(a) || /^[\w-]+:=/.test(a)) data = true;
    }
  }
  if (!url) url = args.find((a) => /^(?:[\w-]+\.)+[a-z]{2,}(?::\d+)?(?:\/|$)|^localhost(?::\d+)?/i.test(a)) ?? '';
  return { method: (method ?? (data ? 'POST' : 'GET')).toUpperCase(), url, bareStatus };
}

// ---- a whole command ----------------------------------------------------------------------------------------
export function analyzeCommand(command, { powershell = false } = {}) {
  const result = { families: new Set(), isRead: true, isEcho: false, isOp: false, dry: false, http: null, programs: [], subs: [] };
  const visit = (cmd, depth) => {
    for (const segment of splitSegments(cmd, { powershell })) {
      const c = classifyCommand(tokenize(segment));
      if (c.inner && depth < 3) { visit(c.inner, depth + 1); continue; }
      if (c.neutral) continue;
      if (c.dry) { c.read = true; result.dry = true; }                 // a dry run is preparation: it can settle nothing
      if (c.prog) { result.programs.push(c.prog); if (c.sub) result.subs.push(c.sub); }
      for (const f of c.families) result.families.add(f);
      if (c.echo) result.isEcho = true;
      if (!c.read) result.isOp = true;
      if (c.http && !result.http) result.http = c.http;
    }
  };
  visit(String(command ?? ''), 0);
  result.isRead = !result.isOp;
  return result;
}

// Does the command run only a part of a test suite? A filter flag (-k, --grep, --filter ...), a single test file or
// test id, or one package ("go test ./pkg"). A whole directory ("pytest tests/") or "./..." is not scoped.
export function isScopedRun(command) {
  const s = String(command ?? '')
    .replace(/\bpython\d?(?:\.\d+)?\s+-m\s+(\w+)/g, 'python MODULE-$1')
    .replace(/\bnode\b([^|;&\n]*?)\s--test(?=\s|=|$)/g, 'node$1 TESTRUN');
  if (/(?:^|\s)(?:-k|-m|--grep|-g|--filter|--testNamePattern|-t|--test-name-pattern|--testPathPattern|--onlyChanged|--changedSince|--lf|--last-failed|--ff|--failed-first|--deselect|--ignore|--only|--lib|--bin|--tests|--package|-p|-run|-Dtest)(?:[\s=]|$)/.test(s)) return true;
  if (/\bcargo\b[^|;&\n]*\s--test(?:\s|=)\S/.test(s)) return true;
  if (/(?:^|\s)[\w./\-]+::[\w[\]-]+/.test(s)) return true;
  if (/(?:^|\s)[\w./\-]+\.(?:py|js|mjs|cjs|ts|tsx|jsx|rb|php|java)(?=\s|$)/.test(s) && /\b(?:pytest|py\.test|jest|vitest|mocha|rspec|phpunit|node|deno|bun|python\d?|py)\b|MODULE-\w+|TESTRUN/.test(s)) return true;
  if (/\bgo\s+test\b/.test(s)) {
    const rest = s.replace(/\s\.\/\.\.\.(?=\s|$)/g, ' ');
    if (/\s\.\/[\w./-]*[\w-](?:\/\.\.\.)?(?=\s|$)/.test(rest)) return true;
  }
  return false;
}
