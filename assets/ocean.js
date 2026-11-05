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

// Clams on the sea floor: one for each person following Shoal on GitHub.
(async () => {
  const section = document.getElementById('clams');
  const bed = document.getElementById('clam-bed');
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
  // Everyone keeps the same clam between visits, because it grows from their name.
  function seeded(text) {
    let h = 2166136261;
    for (const c of text) h = Math.imul(h ^ c.codePointAt(0), 16777619);
    return () => { h = Math.imul(h ^ (h >>> 15), 2246822507) ^ Math.imul(h ^ (h >>> 13), 3266489909); return ((h ^= h >>> 16) >>> 0) / 4294967296; };
  }
  function svgElement(tag, attributes = {}) {
    const node = document.createElementNS(NS, tag);
    for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, value);
    return node;
  }
  // A standing scallop fan: notches and straight ribs meet at the bottom hinge.
  function shellFan(count) {
    const fan = svgElement('g', { class: 'clam-upper' });
    const edge = [];
    for (let i = 0; i <= count; i++) {
      const angle = Math.PI * i / count;
      edge.push([50 - 44 * Math.cos(angle), 84 - 74 * Math.sin(angle)]);
    }
    let d = 'M50 84L6 84';
    for (let i = 1; i <= count; i++) {
      const angle = Math.PI * (i - .5) / count;
      const [x, y] = edge[i];
      // Each quadratic bulges outward between two notches, one bump per rib.
      d += `Q${50 - 49 * Math.cos(angle)} ${84 - 80 * Math.sin(angle)} ${x} ${y}`;
    }
    d += 'L50 84Z';
    fan.append(svgElement('path', { class: 'clam-shell', d }));
    fan.append(svgElement('path', { class: 'clam-mouth', d, transform: 'translate(50 84) scale(.82) translate(-50 -84)' }));
    for (let i = 1; i < count; i++) {
      const [x, y] = edge[i];
      fan.append(svgElement('path', { class: 'clam-rib', d: `M50 84L${x} ${y}` }));
    }
    return fan;
  }
  function shellBowl() {
    const bowl = svgElement('g', { class: 'clam-lower' });
    bowl.append(svgElement('path', { class: 'clam-shell', d: 'M8 76Q50 116 92 76Q50 82 8 76Z' }));
    for (const x of [22, 36, 50, 64, 78]) {
      bowl.append(svgElement('path', { class: 'clam-rib', d: `M${x} 83l${(50 - x) * .16} ${6 - Math.abs(50 - x) * .1}` }));
    }
    return bowl;
  }
  function alignName(link) {
    const name = link.querySelector('.clam-name');
    name.style.setProperty('--name-shift', '0px');
    const bounds = name.getBoundingClientRect();
    const shift = Math.max(8 - bounds.left, Math.min(0, document.documentElement.clientWidth - 8 - bounds.right));
    name.style.setProperty('--name-shift', `${shift}px`);
  }
  function clam(person, index) {
    const random = seeded(person.login);
    const link = document.createElement('a');
    link.className = 'clam';
    link.href = person.url;
    link.setAttribute('aria-label', `${person.login} on GitHub`);
    link.style.setProperty('--clam', `${88 + Math.round(random() * 20)}px`);
    link.style.setProperty('--breath', `${6 + random() * 5}s`);
    link.style.setProperty('--delay', `${-random() * 11}s`);
    link.style.setProperty('--bubble-time', `${12 + random() * 12}s`);
    link.style.setProperty('--bubble-delay', `${-random() * 24}s`);
    link.style.setProperty('--arrival-delay', `${(index % 8) * .09}s`);
    link.style.setProperty('--clam-tint', ['var(--reef-leaf)', 'var(--reef-coral)', 'var(--reef-back)'][Math.floor(random() * 3)]);
    const ribs = 7 + Math.floor(random() * 4);
    const svg = svgElement('svg', { class: 'clam-back', viewBox: '0 0 100 100', 'aria-hidden': 'true', focusable: 'false' });
    const reveal = svgElement('g', { class: 'clam-reveal' });
    const lid = svgElement('g', { class: 'clam-lid' });
    const breath = svgElement('g', { class: 'clam-lid-breath' });
    breath.append(shellFan(ribs));
    lid.append(breath);
    reveal.append(lid);
    svg.append(reveal);
    const front = svgElement('svg', { class: 'clam-front', viewBox: '0 0 100 100', 'aria-hidden': 'true', focusable: 'false' });
    front.append(shellBowl());
    const pearl = document.createElement('span');
    pearl.className = 'clam-pearl';
    pearl.setAttribute('aria-hidden', 'true');
    const face = new Image();
    face.src = `${person.avatar}${person.avatar.includes('?') ? '&' : '?'}s=96`;
    face.alt = '';
    face.width = face.height = 48;
    face.loading = 'lazy';
    face.decoding = 'async';
    face.referrerPolicy = 'no-referrer';
    face.addEventListener('error', () => { face.hidden = true; });
    const gleam = document.createElement('span');
    gleam.className = 'clam-pearl-gleam';
    pearl.append(face, gleam);
    const bubble = document.createElement('span');
    bubble.className = 'clam-bubble';
    bubble.setAttribute('aria-hidden', 'true');
    const name = document.createElement('span');
    name.className = 'clam-name';
    name.textContent = person.login;
    link.append(svg, pearl, front, bubble, name);
    link.addEventListener('pointerenter', () => alignName(link));
    link.addEventListener('focus', () => alignName(link));
    link.addEventListener('animationend', event => {
      if (event.animationName === 'clam-arrival') link.classList.remove('clam-arriving');
    });
    return link;
  }

  bed.append(...people.slice(0, MOST).map(clam));
  if (people.length > MOST) {
    const more = document.createElement('a');
    more.className = 'clam-more';
    more.href = 'https://github.com/orgs/ShoalApps/followers';
    more.textContent = `and ${people.length - MOST} more`;
    bed.append(more);
  }
  const note = document.getElementById('clams-title');
  note.textContent = people.length === 1 ? 'One pearl on our sea floor. ' : `${people.length} pearls on our sea floor. `;
  const join = document.createElement('a');
  join.href = 'https://github.com/ShoalApps';
  join.textContent = 'Follow Shoal on GitHub to add yours';
  note.append(join);
  section.hidden = false;
  window.addEventListener('resize', () => {
    bed.querySelectorAll('.clam:hover, .clam:focus').forEach(alignName);
  });
  if ('IntersectionObserver' in window) {
    const arrival = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        entry.target.classList.add('clam-arriving');
        arrival.unobserve(entry.target);
      }
    }, { threshold: .25 });
    bed.querySelectorAll('.clam').forEach(link => arrival.observe(link));
  }
})();
