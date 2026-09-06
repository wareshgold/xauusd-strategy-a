import { spawn } from 'node:child_process';

const scripts = [
  'analyze-ny-sell-correction-trigger-lineage-audit.mjs',
  'analyze-ny-sell-setup-freshness-age-audit.mjs',
  'analyze-ny-sell-correction-path-geometry-v2.mjs',
];

for (const script of scripts) {
  console.log(`\n>>> RUN ${script}`);
  await new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [`scripts/${script}`], { stdio: 'inherit', shell: false });
    child.on('error', reject);
    child.on('exit', (code) => code === 0 ? resolve() : reject(new Error(`${script} exited with code ${code}`)));
  });
}

console.log('\nNY SELL RESEARCH BATCH COMPLETE.');
console.log('Fresh Holdout remained locked; no production detector/rule changes were made.');
