#!/usr/bin/env node
// sign-token.mjs: signs a Main Team API token (HS256) from your own credentials. Node 18+, no packages.
//
//   MTO_API_KEY=key_... MTO_API_SECRET=... node sign-token.mjs [--env sandbox|production] [--ttl 900]
//   MTO_API_KEY=key_... node sign-token.mjs --secret-file ./secret.txt
//
// Prints only the token on stdout; everything else goes to stderr. The secret is read from the
// environment or from a file, never from the command line, where it would end up in shell history
// and process lists. --iat fixes the issued-at time, for tests only.

import { createHmac } from 'node:crypto';
import { readFileSync, realpathSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

export const BASE_URLS = Object.freeze({
  production: 'https://api.main-team.org/v1',
  sandbox: 'https://apisnd.main-team.org/v1',
});
export const API_KEY_PATTERN = /^key_[A-Za-z0-9_-]{24}$/;
export const MAX_TTL = 3600;
/** An argument that is an apiSecret, alone or as `NAME=value`; a file path merely naming one is not. */
export const SECRET_ARGUMENT = /(?:^|[=\s])secret_[A-Za-z0-9_-]{16,}(?:\s|$)/;

const base64url = (value) => Buffer.from(value).toString('base64url');

/**
 * An HS256 token the API accepts: `kid` and `sub` are the apiKey, `iat` and `exp` are whole seconds,
 * and `exp - iat` is at most 3600.
 */
export function signToken({ apiKey, apiSecret, ttl = 900, iat = Math.floor(Date.now() / 1000) }) {
  if (!API_KEY_PATTERN.test(apiKey ?? '')) throw new Error('the apiKey is not in the issued format (key_ and 24 characters)');
  if (typeof apiSecret !== 'string' || apiSecret === '') throw new Error('the apiSecret is missing');
  if (!Number.isInteger(ttl) || ttl < 1 || ttl > MAX_TTL) throw new Error(`the lifetime must be 1 to ${MAX_TTL} seconds`);
  if (!Number.isInteger(iat) || iat < 0) throw new Error('iat must be whole seconds since the epoch');
  const header = base64url(JSON.stringify({ alg: 'HS256', typ: 'JWT', kid: apiKey }));
  const payload = base64url(JSON.stringify({ sub: apiKey, iat, exp: iat + ttl }));
  const signature = createHmac('sha256', Buffer.from(apiSecret, 'utf8')).update(`${header}.${payload}`).digest('base64url');
  return `${header}.${payload}.${signature}`;
}

/** The secret as the file holds it, less one trailing line break an editor may have added. */
export function readSecretFile(path) {
  const text = readFileSync(path, 'utf8');
  return text.replace(/\r?\n$/, '');
}

function parseArgs(argv) {
  if (argv.some((arg) => SECRET_ARGUMENT.test(arg))) {
    throw new Error('never put the apiSecret on the command line: use MTO_API_SECRET or --secret-file');
  }
  const options = { env: 'sandbox', ttl: 900 };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const value = () => {
      if (i + 1 >= argv.length) throw new Error(`${arg} needs a value`);
      i += 1;
      return argv[i];
    };
    if (arg === '--env') options.env = value();
    else if (arg === '--ttl') options.ttl = Number(value());
    else if (arg === '--secret-file') options.secretFile = value();
    else if (arg === '--iat') options.iat = Number(value());
    else if (arg === '--help' || arg === '-h') options.help = true;
    else throw new Error(`unknown option ${arg}`);
  }
  if (!Object.hasOwn(BASE_URLS, options.env)) throw new Error('--env is sandbox or production');
  return options;
}

const USAGE = `Usage: MTO_API_KEY=key_... MTO_API_SECRET=... node sign-token.mjs [--env sandbox|production] [--ttl seconds]
       MTO_API_KEY=key_... node sign-token.mjs --secret-file <path>
Prints a token for the Authorization header ("Bearer <token>"). Use the credentials of the
environment you call: sandbox credentials are refused by production, and the other way round.`;

function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    process.stderr.write(`${USAGE}\n`);
    return;
  }
  const apiKey = (process.env.MTO_API_KEY ?? '').trim();
  const apiSecret = options.secretFile ? readSecretFile(options.secretFile) : process.env.MTO_API_SECRET;
  if (apiSecret !== undefined && apiSecret !== apiSecret.trim()) {
    process.stderr.write('warning: the apiSecret has spaces or line breaks around it; the API compares it exactly\n');
  }
  const token = signToken({ apiKey, apiSecret, ttl: options.ttl, ...(options.iat !== undefined ? { iat: options.iat } : {}) });
  process.stderr.write(`Token for ${options.env} (${BASE_URLS[options.env]}), valid ${options.ttl} s.\n`);
  process.stdout.write(`${token}\n`);
}

const direct = process.argv[1] && realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url));
if (direct) {
  try {
    main();
  } catch (error) {
    process.stderr.write(`sign-token: ${error.message}\n${USAGE}\n`);
    process.exit(1);
  }
}
