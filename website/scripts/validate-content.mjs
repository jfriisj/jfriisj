import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join, resolve } from 'node:path';
const root = resolve(import.meta.dirname, '..');
let errors = [];
for (const group of ['projects', 'publications']) {
  const dir = join(root, 'src', 'content', group);
  for (const file of readdirSync(dir).filter(f => f.endsWith('.md'))) {
    const source = readFileSync(join(dir, file), 'utf8');
    if (!source.startsWith('---\n') || !source.includes('\n---\n')) errors.push(group + '/' + file + ': missing frontmatter');
    const match = source.match(/^pdf:\s*["']?([^\s"']+)["']?\s*$/m);
    if (!match) continue;
    const pdf = match[1];
    if (!/^\/documents\/[a-z0-9/_-]+\.pdf$/.test(pdf) || pdf.includes('..')) {
      errors.push(group + '/' + file + ': invalid PDF path');
      continue;
    }
    const location = join(root, 'public', pdf.slice(1));
    if (!existsSync(location)) { errors.push(group + '/' + file + ': missing file ' + pdf); continue; }
    const header = readFileSync(location).subarray(0, 5).toString();
    if (header !== '%PDF-') errors.push(group + '/' + file + ': not a PDF file');
  }
}
if (errors.length) {
  for (const error of errors) console.error(error);
  process.exit(1);
}
console.log('Content links and local PDFs validated');
