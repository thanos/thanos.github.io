#!/usr/bin/env node
/**
 * Pack then LLM-generate a resume flavor.
 * Usage: npm run resume:flavor -- --brief <slug>
 */
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '../..');
const args = process.argv.slice(2);

function run(script) {
  const r = spawnSync(process.execPath, [path.join(__dirname, script), ...args], {
    cwd: root,
    stdio: 'inherit',
    env: process.env,
  });
  if (r.status !== 0) process.exit(r.status ?? 1);
}

run('pack.mjs');
run('generate.mjs');
