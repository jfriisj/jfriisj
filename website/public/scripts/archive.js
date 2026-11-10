(() => {
  const input = document.querySelector('[data-search]');
  const buttons = [...document.querySelectorAll('[data-filter]')];
  const entries = [...document.querySelectorAll('[data-archive-item]')];
  const empty = document.querySelector('[data-no-results]');
  const count = document.querySelector('[data-result-count]');
  let active = 'alle';
  const filter = () => {
    const text = (input?.value || '').trim().toLocaleLowerCase('da-DK');
    let visible = 0;
    for (const item of entries) {
      const show = (active === 'alle' || item.dataset.kind === active) &&
        (item.dataset.searchText || '').includes(text);
      item.hidden = !show;
      if (show) visible++;
    }
    if (empty) empty.hidden = visible !== 0 || entries.length === 0;
    if (count) count.textContent = visible + ' af ' + entries.length + ' vist';
  };
  buttons.forEach(button => button.addEventListener('click', () => {
    active = button.dataset.filter;
    buttons.forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    filter();
  }));
  input?.addEventListener('input', filter);
  filter();
})();
