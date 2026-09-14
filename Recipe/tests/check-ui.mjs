import { execFileSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { build } from 'esbuild';
const directory = mkdtempSync(join(tmpdir(), 'recipe-ui-'));
try {
  const fixture = execFileSync('../.venv/bin/python', ['-c', 'from recipe.research import catalog,result; from recipe.database import overview; import json; c=catalog(); print(json.dumps({"catalog":c,"results":[result(s["strategy_id"]) for s in c["strategies"] if s["ready"]],"database":overview()}))'], {maxBuffer: 30 * 1024 * 1024});
  const path = join(directory, 'fixture.json'); writeFileSync(path, fixture);
  const bundle = join(directory, 'check.cjs');
  await build({entryPoints:['tests/render-check.tsx'],bundle:true,platform:'node',format:'cjs',jsx:'automatic',outfile:bundle,loader:{'.css':'empty'},logLevel:'warning'});
  execFileSync(process.execPath, [bundle], {stdio:'inherit',env:{...process.env,RECIPE_CHECK_FIXTURE:path}});
} finally { rmSync(directory, {recursive:true,force:true}); }
