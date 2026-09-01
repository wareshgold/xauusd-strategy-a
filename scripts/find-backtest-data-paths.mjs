import { readdir } from 'node:fs/promises';
import { resolve } from 'node:path';
const ROOT=process.cwd();
async function walk(dir,depth=0){if(depth>4)return[];let out=[];for(const e of await readdir(dir,{withFileTypes:true})){if(['node_modules','.git','dist'].includes(e.name))continue;const p=resolve(dir,e.name);if(e.isDirectory())out.push(...await walk(p,depth+1));else if(/\.json$/.test(e.name))out.push(p)}return out}
const files=await walk(ROOT);console.log(files.filter(p=>/candle|market|data|ohlc|price/i.test(p)).join('\n'));
