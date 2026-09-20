#!/usr/bin/env node
// validate.mjs: checks the Main Team agent kit's format. Node 18+, no packages.
//
//   node kit/scripts/validate.mjs kit          (in this repository, on the templates)
//   node scripts/validate.mjs .                (in the published kit, on the rendered manifests)
//
// The directory is the kit's root. It checks the skills (portable frontmatter, names, size budgets,
// links), the plugin manifests (valid JSON, one plugin name, one version, the one MCP address) and
// that nothing looks like a credential or a local address. It prints every problem and exits 1 when
// there is one. It changes nothing, and it reads no network.

import { existsSync, lstatSync, readdirSync, readFileSync, realpathSync } from 'node:fs';
import { dirname, join, posix, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

export const BUDGETS = Object.freeze({
  description: 1024,
  compatibility: 500,
  bodyLines: 250,
  bodyChars: 14000,
  referenceLines: 400,
  contentsAfter: 100,
  scriptLines: 300,
  files: 20,
  bytes: 256 * 1024,
});
export const FRONTMATTER_KEYS = Object.freeze(['name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools']);
export const PLUGIN_NAME = 'main-team';
/** The one address a manifest may name. There is no sandbox server and never was one. */
export const MCP_ADDRESSES = Object.freeze(['https://mcp.main-team.org/mcp']);
/** Each manifest a release carries, by the template in manifests/ it is rendered from. */
export const TEMPLATES = Object.freeze({
  'manifests/claude-plugin.json.tmpl': '.claude-plugin/plugin.json',
  'manifests/claude-marketplace.json.tmpl': '.claude-plugin/marketplace.json',
  'manifests/claude-mcp.json.tmpl': '.mcp.json',
  'manifests/codex-plugin.json.tmpl': '.codex-plugin/plugin.json',
  'manifests/codex-marketplace.json.tmpl': '.agents/plugins/marketplace.json',
  'manifests/cursor-plugin.json.tmpl': '.cursor-plugin/plugin.json',
  'manifests/gemini-extension.json.tmpl': 'gemini-extension.json',
  'manifests/plugin.json.tmpl': 'plugin.json',
  'manifests/mcp.json.tmpl': 'mcp.json',
  'manifests/server.json.tmpl': 'server.json',
});
export const MANIFESTS = Object.freeze(Object.values(TEMPLATES));
/** The values a template may use: `{{name}}` inside a JSON string. */
export const PLACEHOLDER_NAMES = Object.freeze(['version', 'mcp_url']);
const SAMPLE = Object.freeze({ version: '0.0.0', mcp_url: MCP_ADDRESSES[0] });

/** A template with its placeholders filled; the values are JSON-escaped. */
export function renderTemplate(text, values) {
  return text.replace(/\{\{([a-z_]+)\}\}/g, (all, key) => {
    if (!PLACEHOLDER_NAMES.includes(key) || typeof values[key] !== 'string') throw new Error(`unknown placeholder {{${key}}}`);
    return JSON.stringify(values[key]).slice(1, -1);
  });
}

const NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const SEMVER = /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/;
const SUSPICIOUS = [
  [/secret_[A-Za-z0-9_-]{16,}/, 'a value shaped like an account secret'],
  [/\beyJ[\w-]{10,}\.eyJ/, 'a JSON Web Token'],
  [/-----BEGIN [A-Z ]*PRIVATE KEY-----/, 'a private key'],
  [/(?:\b(?:https?|wss?):)?\/\/(?:localhost|127(?:\.\d{1,3}){3}|0\.0\.0\.0|\[::1\])(?=[:/"'\s<>?#)]|$)/i, 'a local address'],
];

/** Every file under `root` (dot files included, .git aside), with `/` separators. */
export function listFiles(root) {
  const out = [];
  const walk = (dir) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (entry.name === '.git' || entry.name === 'node_modules') continue;
      const path = join(dir, entry.name);
      if (entry.isDirectory()) walk(path);
      else out.push(relative(root, path).split(sep).join('/'));
    }
  };
  walk(root);
  return out.sort();
}

function scalar(raw, where) {
  const value = raw.trim();
  if (value.startsWith('"')) {
    if (!value.endsWith('"') || value.length < 2) throw new Error(`${where}: unterminated "..." value`);
    return JSON.parse(value);
  }
  if (value.startsWith("'")) {
    if (!value.endsWith("'") || value.length < 2) throw new Error(`${where}: unterminated '...' value`);
    return value.slice(1, -1).replace(/''/g, "'");
  }
  if (/^[|>[{&*!%@`]/.test(value) || /:\s/.test(value) || /\s#/.test(value)) {
    throw new Error(`${where}: write this value in double quotes`);
  }
  return value;
}

/** The portable frontmatter subset: `key: value`, and one nested map (`metadata:`). */
export function parseFrontmatter(text) {
  const match = /^---\n([\s\S]*?)\n---\n/.exec(text.replace(/\r\n?/g, '\n'));
  if (!match) throw new Error('SKILL.md must start with a --- frontmatter block');
  const data = {};
  let map = null;
  match[1].split('\n').forEach((line, index) => {
    const where = `frontmatter line ${index + 2}`;
    if (!line.trim() || line.trimStart().startsWith('#')) return;
    const nested = /^ {2}([A-Za-z0-9_-]+):\s+(.*)$/.exec(line);
    if (nested) {
      if (!map) throw new Error(`${where}: an indented line outside a map`);
      map[nested[1]] = scalar(nested[2], where);
      return;
    }
    const pair = /^([A-Za-z0-9_-]+):(?:\s+(.*))?$/.exec(line);
    if (!pair) throw new Error(`${where}: not a "key: value" line`);
    if (Object.hasOwn(data, pair[1])) throw new Error(`${where}: ${pair[1]} is given twice`);
    if (pair[2] === undefined || pair[2].trim() === '') {
      map = data[pair[1]] = {};
      return;
    }
    map = null;
    data[pair[1]] = scalar(pair[2], where);
  });
  return { data, body: text.slice(match[0].length), bodyLine: match[0].split('\n').length };
}

const lines = (text) => text.replace(/\n$/, '').split('\n').length;

/** Relative link targets in Markdown, outside code blocks and code spans. */
function relativeLinks(text) {
  const out = [];
  let fence = false;
  for (const line of text.split('\n')) {
    if (/^\s*(```|~~~)/.test(line)) fence = !fence;
    if (fence) continue;
    for (const [, target] of line.replace(/`[^`]*`/g, '').matchAll(/\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g)) {
      if (!/^(?:[a-z]+:|#)/i.test(target)) out.push(target.split('#')[0]);
    }
  }
  return out;
}

function checkSkill(root, name, files, problems) {
  const at = (msg) => problems.push(`skills/${name}: ${msg}`);
  const own = files.filter((f) => f.startsWith(`skills/${name}/`)).map((f) => f.slice(`skills/${name}/`.length));
  if (!NAME.test(name) || name.length > 64) at('the directory name must be kebab-case, at most 64 characters');
  if (/claude|anthropic/i.test(name)) at('the name must not contain "claude" or "anthropic"');
  if (!own.includes('SKILL.md')) return at('SKILL.md is missing');
  if (own.length > BUDGETS.files) at(`${own.length} files (at most ${BUDGETS.files})`);
  let bytes = 0;
  for (const file of own) {
    if (file.split('/').some((segment) => /^[.-]/.test(segment))) at(`${file}: no path segment may start with a dot or a dash`);
    bytes += lstatSync(join(root, 'skills', name, file)).size;
  }
  if (bytes > BUDGETS.bytes) at(`${bytes} bytes (at most ${BUDGETS.bytes})`);
  const text = readFileSync(join(root, 'skills', name, 'SKILL.md'), 'utf8');
  let parsed;
  try {
    parsed = parseFrontmatter(text);
  } catch (error) {
    return at(`SKILL.md: ${error.message}`);
  }
  const { data, body } = parsed;
  for (const key of Object.keys(data)) if (!FRONTMATTER_KEYS.includes(key)) at(`SKILL.md: frontmatter key "${key}" is not portable`);
  if (data.name !== name) at(`SKILL.md: name "${data.name}" is not the directory's`);
  const description = typeof data.description === 'string' ? data.description.trim() : '';
  if (!description) at('SKILL.md: description is required');
  if (description.length > BUDGETS.description) at(`SKILL.md: description is ${description.length} characters (at most ${BUDGETS.description})`);
  if (/<[^>]*>/.test(description)) at('SKILL.md: description must not contain tags');
  if (/^(?:I|You|We)\b/.test(description)) at('SKILL.md: write the description in the third person');
  if (data.compatibility !== undefined && (typeof data.compatibility !== 'string' || data.compatibility.length > BUDGETS.compatibility)) {
    at(`SKILL.md: compatibility is text of at most ${BUDGETS.compatibility} characters`);
  }
  if (data.license !== undefined && typeof data.license !== 'string') at('SKILL.md: license is text');
  if (data.metadata !== undefined && (typeof data.metadata !== 'object' || Object.values(data.metadata).some((v) => typeof v !== 'string'))) {
    at('SKILL.md: metadata maps names to strings');
  }
  if (lines(body) > BUDGETS.bodyLines) at(`SKILL.md: the body has ${lines(body)} lines (at most ${BUDGETS.bodyLines})`);
  if (body.length > BUDGETS.bodyChars) at(`SKILL.md: the body has ${body.length} characters (at most ${BUDGETS.bodyChars})`);
  const linked = new Set();
  for (const target of relativeLinks(body)) {
    const path = posix.normalize(target);
    if (path.startsWith('..') || !own.includes(path)) at(`SKILL.md: the link ${target} goes to no file of this skill`);
    linked.add(path);
  }
  for (const file of own) {
    const content = readFileSync(join(root, 'skills', name, file), 'utf8');
    if (file.startsWith('references/')) {
      if (!linked.has(file)) at(`${file} is not linked from SKILL.md`);
      if (lines(content) > BUDGETS.referenceLines) at(`${file}: ${lines(content)} lines (at most ${BUDGETS.referenceLines})`);
      if (lines(content) > BUDGETS.contentsAfter && !/^## Contents$/m.test(content.split('\n').slice(0, 40).join('\n'))) {
        at(`${file}: over ${BUDGETS.contentsAfter} lines, so it needs a "## Contents" section near the top`);
      }
      for (const target of relativeLinks(content)) at(`${file}: links to ${target}; references stay one level deep`);
    }
    if (file.startsWith('scripts/')) {
      if (lines(content) > BUDGETS.scriptLines) at(`${file}: ${lines(content)} lines (at most ${BUDGETS.scriptLines})`);
      if (!body.includes(file)) at(`${file} is not mentioned in SKILL.md`);
    }
  }
  for (const [, found] of body.matchAll(/\b((?:scripts|assets)\/[A-Za-z0-9._-]+)/g)) {
    const mention = found.replace(/\.+$/, '');
    if (!own.includes(mention)) at(`SKILL.md mentions ${mention}, which is not in the skill`);
  }
}

/** Every string in `value` that looks like an MCP endpoint. */
function urlsIn(value, out = []) {
  if (typeof value === 'string' && /^https?:\/\/[^\s"]*\/mcp(?:[/?#]|$)/.test(value)) out.push(value);
  else if (value && typeof value === 'object') Object.values(value).forEach((v) => urlsIn(v, out));
  return out;
}

function checkManifest(file, json, problems) {
  const at = (msg) => problems.push(`${file}: ${msg}`);
  const names = [json.name, ...(json.plugins ?? []).map((p) => p.name)].filter((n) => n !== undefined);
  if (file === 'server.json') {
    if (json.name !== 'org.main-team/mcp') at('name must be org.main-team/mcp');
    if (typeof json.description !== 'string' || json.description.length > 100) at('description is at most 100 characters');
  } else if (!names.every((n) => n === PLUGIN_NAME)) at(`every name must be ${PLUGIN_NAME}`);
  const endpoints = urlsIn(json);
  for (const url of endpoints) if (!MCP_ADDRESSES.includes(url)) at(`${url} is not the MCP address`);
  if (/mcp|marketplace|extension/.test(file) && JSON.stringify(json).includes('sandbox')) at('the kit names no sandbox server');
  const versions = [json.version, json.metadata?.version, ...(json.plugins ?? []).map((p) => p.version)].filter(Boolean);
  for (const v of versions) if (!SEMVER.test(v)) at(`version ${v} is not x.y.z`);
  return versions;
}

/** Every problem with the kit at `root`, as sentences; [] when it is sound. */
export function validateKit(root) {
  const problems = [];
  const files = listFiles(root);
  for (const file of files) {
    const path = join(root, file);
    if (lstatSync(path).isSymbolicLink()) { problems.push(`${file}: a symbolic link`); continue; }
    const data = readFileSync(path);
    if (data.includes(0)) { problems.push(`${file}: not a text file`); continue; }
    const text = data.toString('utf8');
    if (Buffer.from(text, 'utf8').compare(data) !== 0) problems.push(`${file}: not UTF-8`);
    for (const [pattern, why] of SUSPICIOUS) if (pattern.test(text)) problems.push(`${file}: ${why}`);
  }
  for (const lock of ['package.json', 'package-lock.json', 'npm-shrinkwrap.json', 'bun.lockb', 'yarn.lock']) {
    if (files.includes(lock)) problems.push(`${lock}: the kit's root holds no package files (installers would run them)`);
  }
  const skills = [...new Set(files.filter((f) => f.startsWith('skills/')).map((f) => f.split('/')[1]))];
  if (!skills.length) problems.push('skills/ holds no skill');
  for (const file of files.filter((f) => /^skills\/[^/]+$/.test(f))) problems.push(`${file}: a file directly in skills/`);
  for (const name of skills) checkSkill(root, name, files, problems);

  const exported = existsSync(join(root, '.claude-plugin'));
  // A kit source tree that carries no manifests at all is the API half of the kit: it contributes
  // skills, and the MCP half owns every manifest. This one file is vendored into both repositories
  // byte-for-byte (the assembler refuses on drift), so it has to serve both — and "no manifests here"
  // is a shape, not a fault. A tree that carries SOME manifests is still checked against all of them,
  // because a half-rendered release is exactly what this check exists to catch.
  const skillsOnly = !exported && !files.some((f) => f.startsWith('manifests/'));
  const versions = new Set();
  if (!exported) {
    for (const file of files.filter((f) => f.startsWith('manifests/'))) {
      if (!Object.hasOwn(TEMPLATES, file)) problems.push(`${file}: not a known manifest template`);
    }
  }
  for (const [template, output] of Object.entries(skillsOnly ? {} : TEMPLATES)) {
    const file = exported ? output : template;
    if (!existsSync(join(root, file))) { problems.push(`${file} is missing`); continue; }
    const raw = readFileSync(join(root, file), 'utf8');
    let json;
    try {
      if (exported && /\{\{/.test(raw)) throw new Error('a placeholder was not rendered');
      json = JSON.parse(exported ? raw : renderTemplate(raw, SAMPLE));
    } catch (error) {
      problems.push(`${file}: ${error.message}`);
      continue;
    }
    for (const v of checkManifest(output, json, problems)) versions.add(v);
  }
  if (exported && versions.size > 1) problems.push(`the manifests disagree on the version: ${[...versions].join(', ')}`);
  return problems;
}

const self = fileURLToPath(import.meta.url);
if (process.argv[1] && realpathSync(resolve(process.argv[1])) === realpathSync(self)) {
  const root = process.argv[2] ?? dirname(dirname(self));
  const problems = validateKit(root);
  for (const problem of problems) process.stdout.write(`FAIL  ${problem}\n`);
  process.stdout.write(problems.length ? `${problems.length} problem(s)\n` : 'OK  the agent kit is valid\n');
  process.exit(problems.length ? 1 : 0);
}
