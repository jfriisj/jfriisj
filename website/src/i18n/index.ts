// Locale discovery is file-driven: add a complete locale JSON file and rebuild.
// The Danish root remains canonical; every other JSON filename becomes /<locale>/.
const modules = import.meta.glob('./locales/*.json', { eager: true, import: 'default' }) as Record<string, Record<string, string>>;
export const defaultLocale = 'da';
const dictionaries = Object.fromEntries(Object.entries(modules).map(([path, data]) => {
  const locale = path.split('/').pop()!.replace('.json', '');
  if (!/^[a-z]{2}(?:-[a-z]{2})?$/.test(locale)) throw new Error('Invalid locale filename: ' + locale);
  return [locale, data];
})) as Record<string, Record<string, string>>;
export const locales = Object.keys(dictionaries).sort((a, b) => a === defaultLocale ? -1 : b === defaultLocale ? 1 : a.localeCompare(b));
if (!dictionaries[defaultLocale]) throw new Error('Missing default locale: ' + defaultLocale);
export function assertLocale(locale: string) {
  if (!locales.includes(locale)) throw new Error('Unsupported locale ' + locale);
  return locale;
}
export function translate(locale: string, key: string): string {
  const dictionary = dictionaries[assertLocale(locale)];
  if (typeof dictionary[key] !== 'string') throw new Error('Missing translation ' + locale + ':' + key);
  return dictionary[key];
}
export function dictionary(locale: string) { return dictionaries[assertLocale(locale)]; }
export function pathFor(locale: string, pathname: string): string {
  assertLocale(locale);
  const normalized = '/' + pathname.replace(/^\/+|\/+$/g, '');
  const suffix = normalized === '/' ? '/' : normalized + '/';
  return locale === defaultLocale ? suffix : '/' + locale + (suffix === '/' ? '/' : suffix);
}
export function removeLocale(pathname: string): string {
  const parts = pathname.split('/').filter(Boolean);
  if (parts.length && locales.includes(parts[0]) && parts[0] !== defaultLocale) parts.shift();
  return '/' + (parts.length ? parts.join('/') + '/' : '');
}
export function switchPath(locale: string, pathname: string) { return pathFor(locale, removeLocale(pathname)); }
export function localeName(locale: string) {
  return new Intl.DisplayNames([locale], { type: 'language' }).of(locale) || locale.toUpperCase();
}
