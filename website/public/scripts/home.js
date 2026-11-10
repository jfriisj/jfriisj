const menu = document.querySelector('.menu-toggle');
    const links = document.querySelector('.navlinks');
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const finePointer = window.matchMedia('(pointer:fine)').matches;
    const progress = document.querySelector('.scroll-progress');
    const localizedMenu = document.querySelector('.menu-toggle')?.dataset;
    const openLabel=localizedMenu?.openLabel||'Åbn menu';
    const closeLabel=localizedMenu?.closeLabel||'Luk menu';
    const timeline = document.querySelector('.timeline');
    const projectsGrid = document.querySelector('.projects-grid');
    const projectPosition = document.getElementById('project-position');

    function closeMenu() {
      links.classList.remove('open');
      menu.setAttribute('aria-expanded','false');
      menu.setAttribute('aria-label',openLabel);
    }
    menu.addEventListener('click', () => {
      const expanded = menu.getAttribute('aria-expanded') === 'true';
      menu.setAttribute('aria-expanded', String(!expanded));
      menu.setAttribute('aria-label', expanded ? openLabel : closeLabel);
      links.classList.toggle('open', !expanded);
    });
    links.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && links.classList.contains('open')) {
        closeMenu(); menu.focus();
      }
    });
    document.addEventListener('click', event => {
      if (links.classList.contains('open') && !event.target.closest('.nav')) closeMenu();
    });

    // Reveal content only when IntersectionObserver is supported; otherwise everything remains visible.
    if (!prefersReducedMotion && 'IntersectionObserver' in window) {
      document.documentElement.classList.add('motion-ready');
      const revealObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-visible');
          revealObserver.unobserve(entry.target);
        });
      }, { threshold:.08, rootMargin:'0px 0px 22px 0px' });
      document.querySelectorAll('[data-reveal]').forEach(node => revealObserver.observe(node));
    }

    function updateProjectPosition() {
      const visible = [...projectsGrid.querySelectorAll('.project-card:not([hidden])')];
      if (!visible.length) { projectPosition.textContent='00 / 00'; return; }
      const leadingEdge=projectsGrid.getBoundingClientRect().left+parseFloat(getComputedStyle(projectsGrid).paddingLeft);
      let closest=0, distance=Infinity;
      visible.forEach((card,index) => {
        const candidate=Math.abs(card.getBoundingClientRect().left-leadingEdge);
        if(candidate<distance){distance=candidate;closest=index;}
      });
      projectPosition.textContent=`${String(closest+1).padStart(2,'0')} / ${String(visible.length).padStart(2,'0')}`;
    }
    projectsGrid.addEventListener('scroll', () => requestAnimationFrame(updateProjectPosition), {passive:true});

    function bindFilters(buttonSelector, itemSelector, dataName) {
      const buttons = [...document.querySelectorAll(buttonSelector)];
      const items = [...document.querySelectorAll(itemSelector)];
      buttons.forEach(button => button.addEventListener('click', () => {
        const value = button.dataset[dataName];
        buttons.forEach(b => b.setAttribute('aria-pressed', String(b === button)));
        items.forEach(item => {
          const tags = item.dataset[dataName === 'timelineFilter' ? 'timelineType' : 'projectType'].split(' ');
          const shown = value === 'alle' || tags.includes(value);
          item.hidden = !shown;
          // Reapply entrance motion for the newly visible filtered results.
          if (shown && item.hasAttribute('data-reveal')) item.classList.add('is-visible');
        });
        if (dataName === 'projectFilter') {
          projectsGrid.scrollTo({left:0,behavior:prefersReducedMotion?'auto':'smooth'});
          requestAnimationFrame(updateProjectPosition);
        }
        updateScrollIndicators();
      }));
    }
    bindFilters('[data-timeline-filter]', '.timeline-item', 'timelineFilter');
    bindFilters('[data-project-filter]', '.project-card', 'projectFilter');

    // Active section indication in desktop nav and on the mobile bottom dock.
    const sections=[...document.querySelectorAll('main section[id]')];
    const navAnchors=[...document.querySelectorAll('.navlinks a, .mobile-dock a')];
    function updateScrollIndicators() {
      const maxScroll=Math.max(1,document.documentElement.scrollHeight-window.innerHeight);
      progress.style.setProperty('--page-progress',Math.min(1,Math.max(0,window.scrollY/maxScroll)));
      document.querySelector('.header').classList.toggle('is-scrolled',window.scrollY>20);
      const lineTop=timeline.getBoundingClientRect().top;
      const lineHeight=Math.max(timeline.getBoundingClientRect().height,1);
      const timelineAmount=Math.min(100,Math.max(0,(window.innerHeight*.51-lineTop)/lineHeight*100));
      timeline.style.setProperty('--timeline-progress',timelineAmount+'%');
      const visibleTimeline=[...timeline.querySelectorAll('.timeline-item:not([hidden])')];
      visibleTimeline.forEach(item => {
        const r=item.getBoundingClientRect();
        item.classList.toggle('is-current',r.top<window.innerHeight*.62 && r.bottom>window.innerHeight*.33);
      });
      const anchor=window.innerHeight*.31;
      let active=sections[0]?.id;
      sections.forEach(section => { if(section.getBoundingClientRect().top<=anchor) active=section.id; });
      if(window.innerHeight+window.scrollY>=document.documentElement.scrollHeight-4) active='kontakt';
      navAnchors.forEach(a => {
        if(a.getAttribute('href') === '#'+active || (a.dataset.dock === 'profil' && ['om-mig','kompetencer'].includes(active))) a.setAttribute('aria-current','location');
        else a.removeAttribute('aria-current');
      });
    }
    let scrollQueued=false;
    window.addEventListener('scroll', () => {
      if(scrollQueued) return;
      scrollQueued=true;
      requestAnimationFrame(() => {updateScrollIndicators();scrollQueued=false;});
    },{passive:true});
    window.addEventListener('resize', () => {
      if(window.innerWidth>900)closeMenu();
      updateProjectPosition();updateScrollIndicators();
    });
    updateProjectPosition();updateScrollIndicators();

    // Desktop-only pointer parallax. Touch devices keep the subtle CSS animation instead.
    const heroVisual=document.querySelector('.hero-visual');
    if(finePointer && !prefersReducedMotion) {
      heroVisual.addEventListener('pointermove',e => {
        const bounds=heroVisual.getBoundingClientRect();
        heroVisual.style.setProperty('--pointer-x', ((e.clientX-bounds.left)/bounds.width-.5)*18+'px');
        heroVisual.style.setProperty('--pointer-y', ((e.clientY-bounds.top)/bounds.height-.5)*18+'px');
      });
      heroVisual.addEventListener('pointerleave', () => {
        heroVisual.style.setProperty('--pointer-x','0px');
        heroVisual.style.setProperty('--pointer-y','0px');
      });
    }
