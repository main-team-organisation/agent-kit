#!/usr/bin/env node
// doctor.mjs: checks a Main Team API setup end to end, and says what to fix. Node 18+, no packages.
//
//   MTO_API_KEY=key_... MTO_API_SECRET=... node doctor.mjs [--env sandbox|production]
//   MTO_API_KEY=key_... node doctor.mjs --secret-file ./secret.txt [--env production]
//   node doctor.mjs --offline      checks the credentials' format only, and calls nothing
//
// It calls two read-only routes: the health check and validate-me. It never prints the secret or a
// token, and it changes nothing on the platform.

import { API_KEY_PATTERN, BASE_URLS, readSecretFile, SECRET_ARGUMENT, signToken } from './sign-token.mjs';

const results = [];
const report = (level, text) => {
  results.push(level);
  process.stdout.write(`${{ ok: ' ok ', warn: 'warn', fail: 'FAIL' }[level]}  ${text}\n`);
};

function parseArgs(argv) {
  if (argv.some((arg) => SECRET_ARGUMENT.test(arg))) {
    throw new Error('never put the apiSecret on the command line: use MTO_API_SECRET or --secret-file');
  }
  const options = { env: 'sandbox' };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--env') options.env = argv[++i];
    else if (arg === '--secret-file') options.secretFile = argv[++i];
    else if (arg === '--offline') options.offline = true;
    else if (arg === '--help' || arg === '-h') options.help = true;
    else throw new Error(`unknown option ${arg}`);
  }
  if (!Object.hasOwn(BASE_URLS, options.env ?? '')) throw new Error('--env is sandbox or production');
  return options;
}

function checkCredentials(apiKey, apiSecret) {
  if (!apiKey) report('fail', 'MTO_API_KEY is not set.');
  else if (!API_KEY_PATTERN.test(apiKey)) report('fail', 'MTO_API_KEY is not key_ followed by 24 letters, digits, "_" or "-". Copy it again as issued.');
  else report('ok', `apiKey format (${apiKey.slice(0, 8)}...).`);
  if (apiSecret === undefined || apiSecret === '') report('fail', 'The apiSecret is missing: set MTO_API_SECRET, or pass --secret-file.');
  else if (apiSecret !== apiSecret.trim()) report('fail', 'The apiSecret has spaces or line breaks around it. Use it exactly as issued.');
  else if (!apiSecret.startsWith('secret_')) report('warn', 'The apiSecret does not start with secret_. Check that you copied the whole value.');
  else report('ok', 'apiSecret is present (not shown).');
}

async function call(url, token) {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const res = await fetch(url, { headers, signal: AbortSignal.timeout(15_000) });
  const text = await res.text();
  let body = null;
  try {
    body = JSON.parse(text);
  } catch {
    body = null;
  }
  return { res, body };
}

function checkRoles(account) {
  const roles = Array.isArray(account?.roles) ? account.roles : [];
  report('ok', `${roles.length} role(s) on the account.`);
  const own = (role) => !role.authorized || role.authorized === account._id;
  const grants = (action) => roles.some((r) => r.effect === 'allow' && ['*', '*/*', action, `${action.split('/')[0]}/*`].includes(r.action) && own(r));
  for (const action of ['student/create', 'student/read', 'application/create', 'auth/signin', 'certificate/read', 'report/read']) {
    if (grants(action)) report('ok', `${action}: granted by a role on this account.`);
    else report('warn', `${action}: no role grants it; those operations answer 403 forbidden.`);
  }
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    process.stdout.write('Usage: MTO_API_KEY=... MTO_API_SECRET=... node doctor.mjs [--env sandbox|production] [--secret-file path] [--offline]\n');
    return 0;
  }
  const base = BASE_URLS[options.env];
  const apiKey = (process.env.MTO_API_KEY ?? '').trim();
  const apiSecret = options.secretFile ? readSecretFile(options.secretFile) : process.env.MTO_API_SECRET;
  process.stdout.write(`Main Team API doctor: ${options.env} (${base})\n`);
  checkCredentials(apiKey, apiSecret);
  if (options.offline || results.includes('fail')) return results.includes('fail') ? 1 : 0;

  let health;
  try {
    health = await call(`${base}/health`);
  } catch (error) {
    report('fail', `Cannot reach ${base}/health (${error.message}). Check the network, a proxy or a firewall.`);
    return 1;
  }
  if (health.res.ok) report('ok', 'The API answers the health check.');
  else report('fail', `The health check answered ${health.res.status}.`);

  const serverTime = Date.parse(health.res.headers.get('date') ?? '');
  const skew = Number.isNaN(serverTime) ? null : Math.round((Date.now() - serverTime) / 1000);
  if (skew === null) report('warn', 'The server sent no Date header, so the clock was not compared.');
  else if (Math.abs(skew) > 30) report('fail', `This clock is ${skew} s off the server's. Tokens are refused beyond 30 s: synchronize the clock (NTP).`);
  else if (Math.abs(skew) > 5) report('warn', `This clock is ${skew} s off the server's. Keep it synchronized.`);
  else report('ok', `Clock within ${Math.abs(skew)} s of the server's.`);

  const iat = Math.floor((Number.isNaN(serverTime) ? Date.now() : serverTime) / 1000);
  const token = signToken({ apiKey, apiSecret, ttl: 300, iat });
  const me = await call(`${base}/api-account/validate-me`, token);
  const requestId = me.body?.error?.request_id ?? me.res.headers.get('x-request-id');
  if (me.res.status === 200) {
    report('ok', `Signed in as ${me.body?.companyName ?? 'your account'}; the account is ${me.body?.isActive === false ? 'INACTIVE' : 'active'}.`);
    checkRoles(me.body);
  } else if (me.res.status === 401) {
    report('fail', `401: the token was refused (request_id ${requestId}). Check that the key and secret belong to ${options.env}, are active, and are copied exactly.`);
  } else if (me.res.status === 403) {
    report('fail', `403: the account lacks allow api/* on mto, which validate-me needs (request_id ${requestId}).`);
  } else if (me.res.status === 429) {
    report('warn', `429: rate limited; wait ${me.res.headers.get('retry-after') ?? 60} s.`);
  } else {
    report('fail', `validate-me answered ${me.res.status} (request_id ${requestId}).`);
  }
  return results.includes('fail') ? 1 : 0;
}

main().then(
  (code) => process.exit(code),
  (error) => {
    process.stderr.write(`doctor: ${error.message}\n`);
    process.exit(2);
  },
);
