// Check the static dashboard without needing a browser or third-party packages.
import { readFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';
import vm from 'node:vm';

const base = resolve(import.meta.dirname, '..');
const dashboard = resolve(base, 'python/dashboard/index.html');
const html = readFileSync(dashboard, 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
if (!script) throw new Error('Dashboard script is missing');
new vm.Script(script, { filename: dashboard });

const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]));
for (const [, selector] of script.matchAll(/\$\('#([^']+)'\)/g)) {
  if (!ids.has(selector)) throw new Error(`Missing dashboard element: #${selector}`);
}
for (const path of [
  'experiments/results/multiseed/summary.csv',
  'experiments/results/multiseed/config.json',
  ...['baseline', 'sr', 'aura'].map(mode => `experiments/results/sample/${mode}/events.csv`),
]) {
  if (!existsSync(resolve(base, path))) throw new Error(`Missing dashboard data: ${path}`);
}
console.log('Dashboard script, elements, and measured data paths are valid');
