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
  'experiments/results/ablation/summary.csv',
  'experiments/results/ablation/paired.csv',
  'experiments/results/robustness/summary.csv',
  'experiments/results/robustness/paired.csv',
  'experiments/results/robustness/config.json',
  ...['baseline', 'sr', 'aura'].map(mode => `experiments/results/sample/${mode}/events.csv`),
]) {
  if (!existsSync(resolve(base, path))) throw new Error(`Missing dashboard data: ${path}`);
}
const robustnessSummary = readFileSync(resolve(base, 'experiments/results/robustness/summary.csv'), 'utf8');
for (const key of ['ddr', 'routine_pdr', 'retransmission_overhead', 'background_goodput_bps', 'background_flow_fairness_jain']) {
  if (!robustnessSummary.split('\n', 1)[0].includes(`${key}_mean`)) {
    throw new Error(`Robustness summary is missing ${key}`);
  }
}
const ablationSummary = readFileSync(resolve(base, 'experiments/results/ablation/summary.csv'), 'utf8');
const ablationPairs = readFileSync(resolve(base, 'experiments/results/ablation/paired.csv'), 'utf8');
for (const key of ['ddr', 'retransmission_overhead', 'routine_pdr', 'background_goodput_bps']) {
  if (!ablationSummary.split('\n', 1)[0].includes(`${key}_mean`)) {
    throw new Error(`Ablation summary is missing ${key}`);
  }
  if (!ablationPairs.includes(`,${key},no_feasibility,`)) {
    throw new Error(`Ablation pairs are missing ${key}`);
  }
}
console.log('Dashboard script, elements, and measured data paths are valid');
