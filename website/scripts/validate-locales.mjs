import { readFileSync, readdirSync } from 'node:fs';
import { resolve, join } from 'node:path';

const dir = resolve(import.meta.dirname, '../src/i18n/locales');
const names = readdirSync(dir).filter(name => name.endsWith('.json')).sort();
if (!names.includes('da.json')) throw new Error('Missing da.json default catalog');
if (names.length < 2) throw new Error('At least two locale catalogs are expected');
const catalogs = new Map();
for (const file of names) {
  if (!/^[a-z]{2}(?:-[a-z]{2})?\.json$/.test(file)) throw new Error('Invalid locale filename: ' + file);
  const data = JSON.parse(readFileSync(join(dir, file), 'utf8'));
  if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error(file + ': root must be an object');
  for (const [key, value] of Object.entries(data)) {
    if (!key.trim() || typeof value !== 'string' || !value.trim()) {
      throw new Error(file + ': empty/invalid translation for key ' + key);
    }
  }
  catalogs.set(file, data);
}
const baseline = Object.keys(catalogs.get('da.json')).sort();
const stableKeyPattern = /^[a-z][a-z0-9]*(?:\.[a-z][a-zA-Z0-9]*)+$/;
const stableKeys = baseline.filter(key => stableKeyPattern.test(key));
const accidentalDuplicates = stableKeys.filter(key => !catalogs.get('da.json')[key].trim());
if (accidentalDuplicates.length) throw new Error('Invalid stable translation values: ' + accidentalDuplicates.join(', '));
for (const [file, data] of catalogs) {
  const keys = Object.keys(data);
  const missing = baseline.filter(key => !(key in data));
  const extra = keys.filter(key => !(key in catalogs.get('da.json')));
  if (missing.length || extra.length) throw new Error(
    file + ': locale keys differ from da.json; missing=' + JSON.stringify(missing) + ', extra=' + JSON.stringify(extra)
  );
}
console.log('Validated ' + catalogs.size + ' complete JSON locale catalogs (' + baseline.length + ' keys)');
