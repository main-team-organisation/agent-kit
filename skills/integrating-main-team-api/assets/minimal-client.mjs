// main-team-client.mjs: a minimal Main Team API client (Node.js 20+).
// Generated from the Main Team API contract 1.1.1: the minimal client of
// https://hub.main-team.org/api/clients/build-your-own. Do not edit: it is rebuilt with every release.
import jwt from 'jsonwebtoken';
import { randomUUID } from 'node:crypto';
import { writeFile } from 'node:fs/promises';
import { basename, join } from 'node:path';

const BASE_URL = 'https://api.main-team.org/v1'; // sandbox: 'https://apisnd.main-team.org/v1'
const TOKEN_LIFETIME = 900; // seconds; the API accepts at most 3600
const RENEW_BEFORE = 60;    // sign a new token this long before exp

export class ApiError extends Error {
  constructor(status, body, headers) {
    super(body?.error?.message ?? `HTTP ${status}`);
    this.status = status;
    this.code = body?.error?.code ?? 'unknown';
    this.documentationUrl = body?.error?.documentation_url;
    this.requestId = body?.error?.request_id ?? headers.get('x-request-id');
    this.retryAfter = Number(headers.get('retry-after')) || undefined;
  }
}

export class MainTeamClient {
  #apiKey; #apiSecret; #token = null; #tokenExp = 0;

  constructor({ apiKey, apiSecret }) {
    if (!/^key_[A-Za-z0-9_-]{24}$/.test(apiKey ?? '')) throw new Error('apiKey is not in the issued format');
    if (!apiSecret) throw new Error('apiSecret is missing');
    this.#apiKey = apiKey;
    this.#apiSecret = apiSecret;
  }

  #bearer() {
    const now = Math.floor(Date.now() / 1000);
    if (!this.#token || now >= this.#tokenExp - RENEW_BEFORE) {
      this.#tokenExp = now + TOKEN_LIFETIME;
      this.#token = jwt.sign(
        { sub: this.#apiKey, iat: now, exp: this.#tokenExp }, // iat and exp are both required
        this.#apiSecret,
        { algorithm: 'HS256', keyid: this.#apiKey },          // keyid becomes the kid header
      );
    }
    return this.#token;
  }

  async #send(method, path, { query, body, timeoutMs = 30_000 } = {}) {
    const url = new URL(BASE_URL + path);
    for (const [key, value] of Object.entries(query ?? {})) url.searchParams.set(key, String(value));
    const res = await fetch(url, {
      method,
      headers: {
        Authorization: `Bearer ${this.#bearer()}`,
        'X-Request-Id': randomUUID(),
        ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: AbortSignal.timeout(timeoutMs),
    });
    if (!res.ok) throw new ApiError(res.status, await res.json().catch(() => null), res.headers);
    return res;
  }

  /** A JSON route. Resolves to the envelope: { success, message, data, pagination? }. */
  async request(method, path, options) {
    const json = await (await this.#send(method, path, options)).json();
    // validate-me is the one JSON route that answers without an envelope.
    return path === '/api-account/validate-me' ? { success: true, data: json } : json;
  }

  /** Every item of a paginated list, 100 per page (the maximum). */
  async *paginate(path, query = {}) {
    for (let page = 1; ; page++) {
      const { data, pagination } = await this.request('GET', path, { query: { ...query, page, limit: 100 } });
      yield* data;
      if (!pagination || page >= pagination.totalPages) return;
    }
  }

  /** A certificate or report download. Saves the file and resolves to its name. */
  async download(path, directory = '.') {
    const res = await this.#send('GET', path, { timeoutMs: 120_000 });
    const bytes = Buffer.from(await res.arrayBuffer()); // rejects if the connection drops mid-body
    const expected = Number(res.headers.get('content-length'));
    const decoded = Boolean(res.headers.get('content-encoding')); // then Content-Length is the encoded size
    if (expected && !decoded && bytes.length !== expected) throw new Error('Download ended early');
    const name = basename(fileNameOf(res.headers.get('content-disposition')) ?? 'download.pdf');
    await writeFile(join(directory, name), bytes);
    return name;
  }
}

function fileNameOf(header) {
  const star = /filename\*=UTF-8''([^;]+)/i.exec(header ?? '');
  if (star) return decodeURIComponent(star[1]);
  return /filename="([^"]*)"/i.exec(header ?? '')?.[1] ?? null;
}
