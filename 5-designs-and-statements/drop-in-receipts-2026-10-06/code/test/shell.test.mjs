import { test } from 'node:test';
import assert from 'node:assert/strict';
import { analyzeCommand, splitSegments, tokenize, isScopedRun } from '../src/shell.mjs';

const fam = (command, opts) => [...analyzeCommand(command, opts).families].sort();

test('git: push, merge, pull, commit are told apart from reads', () => {
  assert.deepEqual(fam('git push origin main'), ['push']);
  assert.deepEqual(fam('git -C /tmp/repo push --force-with-lease'), ['push']);
  assert.deepEqual(fam('git merge feature'), ['merge']);
  assert.deepEqual(fam('git pull origin main'), ['merge']);
  assert.deepEqual(fam('git commit -m "fix: a && b; c | d"'), ['commit']);
  assert.deepEqual(fam('git add -A && git commit -m x && git push'), ['commit', 'push']);
  for (const read of ['git status', 'git log --oneline | head -5', 'git diff HEAD~1', 'git branch', 'git remote -v', 'git show abc1234', 'git fetch origin']) {
    const a = analyzeCommand(read);
    assert.equal(a.isRead, true, read);
    assert.deepEqual([...a.families], [], read);
  }
  assert.equal(analyzeCommand('git branch -D old').isRead, false);
  assert.equal(analyzeCommand('git tag v1.0.0').isRead, false);
  assert.equal(analyzeCommand('git remote add x y').isRead, false);
});

test('gh: pr merge, pr create, api with its method', () => {
  assert.deepEqual(fam('gh pr merge 42 --squash'), ['merge']);
  assert.deepEqual(fam('gh pr create --title x --body y'), ['create', 'send']);
  assert.equal(analyzeCommand('gh pr view 42').isRead, true);
  assert.equal(analyzeCommand('gh pr checks 42').isRead, true);
  const api = analyzeCommand('gh api -X PUT /repos/a/b/pulls/42/merge');
  assert.deepEqual([...api.families], ['http']);
  assert.equal(api.http.method, 'PUT');
  assert.equal(analyzeCommand('gh api repos/a/b/issues').http.method, 'GET');
  assert.equal(analyzeCommand('gh api repos/a/b/issues -f title=x').http.method, 'POST');
});

test('test runners: pytest, node --test, npm test, jest, go, cargo, mvn, dotnet, make', () => {
  for (const command of ['pytest -q', 'python -m pytest tests/', 'python3 -m unittest', 'node --test', 'node --test test/foo.test.mjs',
    'npm test', 'npm run test:unit', 'yarn test', 'pnpm test', 'npx jest --coverage', 'go test ./...', 'cargo test', 'mvn -q test', './gradlew test',
    'dotnet test', 'make test', 'bun test', 'rspec', 'bash run_tests.sh', './test.sh', 'python test_foo.py', 'cd app && pytest']) {
    assert.ok(analyzeCommand(command).families.has('test'), command);
  }
  assert.equal(analyzeCommand('pytest -q').isRead, false);
});

test('builds, deploys, installs and sends', () => {
  assert.ok(fam('npm run build').includes('build'));
  assert.ok(fam('pnpm run lint').includes('build'));
  assert.ok(fam('tsc --noEmit').includes('build'));
  assert.ok(fam('cargo build --release').includes('build'));
  assert.ok(fam('go build ./...').includes('build'));
  assert.ok(fam('make').includes('build'));
  assert.ok(fam('npm publish').includes('deploy'));
  assert.ok(fam('docker push acme/app:1.2').includes('deploy'));
  assert.ok(fam('kubectl apply -f k8s/').includes('deploy'));
  assert.ok(fam('helm upgrade app ./chart').includes('deploy'));
  assert.ok(fam('terraform apply -auto-approve').includes('deploy'));
  assert.ok(fam('./deploy.sh prod').includes('deploy'));
  assert.ok(fam('bash scripts/release.sh').includes('deploy'));
  assert.ok(fam('make deploy').includes('deploy'));
  assert.ok(fam('pip install requests').includes('install'));
  assert.ok(fam('npm install left-pad').includes('install'));
  assert.ok(fam('python -m pip install -r requirements.txt').includes('install'));
  assert.ok(fam('mail -s hi dana@example.org').includes('send'));
});

test('reads and echoes never count as operations', () => {
  for (const command of ['cat results.txt', 'grep -r error logs/', 'ls -la', 'tail -n 20 test.log', 'kubectl get pods -n x', 'kubectl -n auth-prod rollout status deployment/web',
    'docker ps', 'npm view left-pad', 'terraform plan', 'pip list', 'echo "15 passed"', 'printf "ok\\n"']) {
    assert.equal(analyzeCommand(command).isRead, true, command);
  }
  assert.equal(analyzeCommand('echo "15 passed"').isEcho, true);
  assert.equal(analyzeCommand('Write-Host "all tests passed"', { powershell: true }).isEcho, true);
  assert.equal(analyzeCommand('sed -i s/a/b/ file.txt').isRead, false);
  // one operating segment anywhere makes the call an operation
  assert.equal(analyzeCommand('cat body.json | curl -X POST https://x.example/api -d @-').isRead, false);
  assert.equal(analyzeCommand('cd app && pytest -q').isOp, true);
  assert.equal(analyzeCommand('cd app').isRead, true);
});

test('curl and friends: method, url, and a bare status request', () => {
  const post = analyzeCommand('curl -s -X POST https://api.example.com/v1/send -d "{}"');
  assert.deepEqual([...post.families], ['http']);
  assert.equal(post.http.method, 'POST');
  assert.equal(post.http.url, 'https://api.example.com/v1/send');
  assert.equal(analyzeCommand('curl https://example.com').http.method, 'GET');
  assert.equal(analyzeCommand('curl -I https://example.com').http.method, 'HEAD');
  assert.equal(analyzeCommand('curl -d x https://example.com').http.method, 'POST');
  assert.equal(analyzeCommand('curl -s -o /dev/null -w "%{http_code}" https://x.example/health').http.bareStatus, true);
  assert.equal(analyzeCommand('Invoke-RestMethod -Uri https://x.example/a -Method Post -Body $b', { powershell: true }).http.method, 'POST');
  assert.equal(analyzeCommand('wget --post-data=a=1 https://x.example/a').http.method, 'POST');
});

test('wrappers and nested shells: sudo, env, timeout, bash -c, cmd /c', () => {
  assert.ok(fam('sudo npm test').includes('test'));
  assert.ok(fam('FOO=1 BAR=2 pytest').includes('test'));
  assert.ok(fam('env CI=1 npm test').includes('test'));
  assert.ok(fam('timeout 60 pytest -q').includes('test'));
  assert.ok(fam('bash -c "cd app && pytest -q"').includes('test'));
  assert.ok(fam('cmd /c "npm test"').includes('test'));
  assert.ok(fam('pwsh -Command "git push origin main"').includes('push'));
  assert.ok(fam('uv run pytest').includes('test'));
});

test('heredoc bodies are data, not commands', () => {
  const command = "cat > notes.txt <<'EOF'\ngit push origin main\nnpm test\nEOF\nls";
  assert.deepEqual(fam(command), []);
  assert.equal(analyzeCommand(command).isRead, true);
  const real = "git commit -m \"$(cat <<'EOF'\nfix: the thing\nEOF\n)\"";
  assert.deepEqual(fam(real), ['commit']);
});

test('splitting respects quotes and redirects', () => {
  assert.deepEqual(splitSegments('echo "a; b" && ls'), ['echo "a; b"', 'ls']);
  assert.deepEqual(splitSegments('pytest 2>&1 | tail -5'), ['pytest 2>&1', 'tail -5']);
  assert.deepEqual(splitSegments('a || b ; c\nd'), ['a', 'b', 'c', 'd']);
  assert.deepEqual(tokenize('git commit -m "two words" \'x y\''), ['git', 'commit', '-m', 'two words', 'x y']);
});

test('isScopedRun: filters and single files are scoped; whole directories and ./... are not', () => {
  for (const c of ['python -m pytest tests/test_one.py', 'pytest -k auth', 'node --test test/foo.test.mjs', 'go test ./pkg/foo', 'cargo test --lib',
    'cargo test -p x', 'cargo test --test integ', 'jest src/a.test.js', 'pytest tests/test_a.py::test_x', 'mvn -q test -Dtest=FooTest']) {
    assert.equal(isScopedRun(c), true, c);
  }
  for (const c of ['pytest', 'python -m pytest', 'pytest tests/', 'node --test', 'node --test test/', 'go test ./...', 'cargo test', 'npm test', 'make test']) {
    assert.equal(isScopedRun(c), false, c);
  }
});

test('a dry run is a read: it can settle nothing, and it is flagged so the card can say so', () => {
  for (const command of [
    'git push --dry-run origin main', 'git push -n origin main', 'git push -fn origin main', 'npm publish --dry-run', 'kubectl apply -f x.yaml --dry-run=client',
    'rsync -avn src/ dst/', 'make -n deploy', 'helm upgrade app ./chart --dry-run', 'aws ec2 run-instances --dry-run', 'ansible-playbook site.yml --check',
    'git commit --dry-run', 'npm run deploy -- --dry-run', 'DRY_RUN=1 ./deploy.sh', 'terraform apply -auto-approve --dry_run', 'az deployment group create --what-if',
    'bash -c "git push --dry-run origin main"',
  ]) {
    const a = analyzeCommand(command);
    assert.equal(a.isRead, true, command);
    assert.equal(a.dry, true, command);
  }
  // the real thing next to a dry run is still an operation
  const both = analyzeCommand('git push --dry-run origin dev && git push origin dev');
  assert.equal(both.isRead, false);
  assert.equal(both.dry, true);
  // flags that only look like dry-run flags are not
  for (const command of ['git commit -n -m x', 'pytest -n 4', 'git push origin main', 'git push --no-verify origin main', 'npm publish', 'kubectl apply -f x.yaml']) {
    assert.equal(analyzeCommand(command).dry, false, command);
    assert.equal(analyzeCommand(command).isRead, false, command);
  }
});
