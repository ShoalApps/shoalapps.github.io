(() => {
  const root = document.documentElement;
  // Progressive enhancement only: navigation itself is ordinary HTML anchors.
  const menu = document.querySelector('.mobile-menu');
  menu?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => { menu.open = false; }));
  menu?.addEventListener('keydown', event => {
    if (event.key === 'Escape') { menu.open = false; menu.querySelector('summary').focus(); }
  });
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const button = document.getElementById('motion-toggle');
  let choice = null;
  try { choice = localStorage.getItem('shoal-motion'); } catch {}
  const cleanups = new Set();
  const canAnimate = () => root.dataset.motion !== 'off' && !reduced.matches;
  function clearEffects() { cleanups.forEach(fn => fn()); }
  function apply() {
    const enabled = !reduced.matches && choice !== 'off';
    root.dataset.motion = enabled ? 'on' : 'off';
    button.setAttribute('aria-pressed', String(enabled));
    button.disabled = reduced.matches;
    button.textContent = reduced.matches ? 'Reduced motion' : enabled ? 'Pause animations' : 'Play animations';
    if (!enabled) clearEffects();
  }
  button.addEventListener('click', () => {
    choice = root.dataset.motion === 'off' ? 'on' : 'off';
    try { localStorage.setItem('shoal-motion', choice); } catch {}
    apply();
  });
  reduced.addEventListener('change', apply);
  apply();
  document.querySelectorAll('.fish-card:not(.archived)').forEach(card => {
    const source = card.querySelector('.icon-source');
    if (!source) return;
    let last = -Infinity;
    function shimmer() {
      if (performance.now() - last < 1900) return;
      last = performance.now();
      source.classList.add('glowing');
      const nodes = [];
      let timer;
      function cleanup() {
        nodes.forEach(el => el.remove());
        source.classList.remove('glowing');
        clearTimeout(timer);
        cleanups.delete(cleanup);
      }
      cleanups.add(cleanup);
      if (canAnimate()) {
        const shine = document.createElement('span');
        shine.className = 'icon-light';
        shine.setAttribute('aria-hidden', 'true');
        source.append(shine); nodes.push(shine);
        for (let i = 0; i < 5; i++) {
          const bubble = document.createElement('span');
          bubble.className = 'icon-bubble';
          bubble.setAttribute('aria-hidden', 'true');
          bubble.style.setProperty('--x', `${12 + Math.random()*70}%`);
          bubble.style.setProperty('--size', `${3 + Math.random()*6}px`);
          bubble.style.setProperty('--delay', `${Math.random()*.35}s`);
          bubble.style.setProperty('--drift', `${Math.random()*24-12}px`);
          source.append(bubble); nodes.push(bubble);
        }
      }
      timer = setTimeout(cleanup, 1900);
    }
    source.addEventListener('pointerenter', e => { if(e.pointerType === 'mouse') shimmer(); });
    card.addEventListener('focusin', shimmer);
    card.addEventListener('pointerdown', e => { if(e.pointerType !== 'mouse') shimmer(); });
  });
  new MutationObserver(() => { if (!canAnimate()) clearEffects(); }).observe(root, {attributes:true,attributeFilter:['data-motion']});
  document.addEventListener('visibilitychange', () => { if(document.hidden) clearEffects(); });
})();

// Sea urchins on the sea floor: one for each person following Shoal on GitHub.
(async () => {
  const section = document.getElementById('urchins');
  const bed = document.getElementById('urchin-bed');
  if (!section || !bed) return;
  const MOST = 200;
  let people = [];
  try { people = await (await fetch('followers.json', { cache: 'no-cache' })).json(); } catch { return; }
  if (!Array.isArray(people)) return;
  // Only GitHub's own addresses: this file decides where links and pictures on the page point.
  people = people.filter(p => p && typeof p.login === 'string'
    && /^https:\/\/github\.com\/[\w.-]+$/.test(p.url) && /^https:\/\/avatars\.githubusercontent\.com\//.test(p.avatar));
  if (!people.length) return;

  const NS = 'http://www.w3.org/2000/svg';
  // Everyone keeps the same urchin between visits, because it grows from their name.
  function seeded(text) {
    let h = 2166136261;
    for (const c of text) h = Math.imul(h ^ c.codePointAt(0), 16777619);
    return () => { h = Math.imul(h ^ (h >>> 15), 2246822507) ^ Math.imul(h ^ (h >>> 13), 3266489909); return ((h ^= h >>> 16) >>> 0) / 4294967296; };
  }
  function spines(random, count, from, shortest, longest, className) {
    let d = '';
    const turn = random() * Math.PI;
    for (let i = 0; i < count; i++) {
      const angle = turn + i / count * Math.PI * 2 + (random() - .5) * .08;
      const reach = shortest + random() * (longest - shortest);
      d += `M${(Math.cos(angle) * from).toFixed(1)} ${(Math.sin(angle) * from).toFixed(1)}L${(Math.cos(angle) * reach).toFixed(1)} ${(Math.sin(angle) * reach).toFixed(1)}`;
    }
    const path = document.createElementNS(NS, 'path');
    path.setAttribute('class', className);
    path.setAttribute('d', d);
    return path;
  }
  function urchin(person) {
    const random = seeded(person.login);
    const link = document.createElement('a');
    link.className = 'urchin';
    link.href = person.url;
    link.setAttribute('aria-label', `${person.login} on GitHub`);
    link.style.setProperty('--urchin', `${70 + Math.round(random() * 18)}px`);
    link.style.setProperty('--sway', `${6 + random() * 4}s`);
    link.style.setProperty('--delay', `${-random() * 8}s`);
    const svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('viewBox', '-50 -50 100 100');
    svg.setAttribute('aria-hidden', 'true');
    svg.append(spines(random, 22, 22, 36, 42, 'spines-back'), spines(random, 26, 24, 40, 49, 'spines'));
    const shell = document.createElementNS(NS, 'circle');
    shell.setAttribute('class', 'shell');
    shell.setAttribute('r', '25');
    svg.append(shell);
    const face = new Image();
    face.src = `${person.avatar}${person.avatar.includes('?') ? '&' : '?'}s=96`;
    face.alt = '';
    face.width = face.height = 48;
    face.loading = 'lazy';
    face.decoding = 'async';
    face.referrerPolicy = 'no-referrer';
    const name = document.createElement('span');
    name.className = 'urchin-name';
    name.textContent = person.login;
    link.append(svg, face, name);
    return link;
  }

  bed.append(...people.slice(0, MOST).map(urchin));
  if (people.length > MOST) {
    const more = document.createElement('a');
    more.className = 'urchin-more';
    more.href = 'https://github.com/orgs/ShoalApps/followers';
    more.textContent = `and ${people.length - MOST} more`;
    bed.append(more);
  }
  const note = document.getElementById('urchins-title');
  note.textContent = people.length === 1 ? 'One follower lives on our sea floor. ' : `${people.length} followers live on our sea floor. `;
  const join = document.createElement('a');
  join.href = 'https://github.com/ShoalApps';
  join.textContent = 'Follow Shoal on GitHub to join them';
  note.append(join);
  section.hidden = false;
})();
