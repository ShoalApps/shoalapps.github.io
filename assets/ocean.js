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
  try {
    const response = await fetch('followers.json', { cache: 'no-cache' });
    if (!response.ok) return;
    people = await response.json();
  } catch { return; }
  if (!Array.isArray(people)) return;
  // Only GitHub's own addresses: this file decides where links and pictures point.
  people = people.filter(p => p && typeof p.login === 'string'
    && /^https:\/\/github\.com\/[\w.-]+$/.test(p.url) && /^https:\/\/avatars\.githubusercontent\.com\//.test(p.avatar));
  if (!people.length) return;

  const NS = 'http://www.w3.org/2000/svg';
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
  function alignName(link) {
    const name = link.querySelector('.clam-name');
    name.style.setProperty('--name-shift', '0px');
    const bounds = name.getBoundingClientRect();
    const shift = Math.max(8 - bounds.left, Math.min(0, document.documentElement.clientWidth - 8 - bounds.right));
    name.style.setProperty('--name-shift', `${shift}px`);
  }
  // Build working pearl links before requesting the optional illustration.
  const clams = people.slice(0, MOST).map((person, index) => {
    const random = seeded(person.login);
    const link = document.createElement('a');
    link.className = 'clam';
    link.href = person.url;
    link.setAttribute('aria-label', `${person.login} on GitHub`);
    link.style.setProperty('--clam', `${152 + Math.round(random() * 24)}px`);
    link.style.setProperty('--clam-wash', ['var(--clam-wash-leaf)', 'var(--clam-wash-coral)', 'var(--clam-wash-sand)'][Math.floor(random() * 3)]);
    const window = document.createElement('span');
    window.className = 'clam-pearl-window';
    window.setAttribute('aria-hidden', 'true');
    const pearl = document.createElement('span');
    pearl.className = 'clam-pearl';
    const face = new Image();
    face.src = `${person.avatar}${person.avatar.includes('?') ? '&' : '?'}s=96`;
    face.alt = '';
    face.width = face.height = 48;
    face.loading = 'lazy';
    face.decoding = 'async';
    face.referrerPolicy = 'no-referrer';
    face.addEventListener('error', () => { face.hidden = true; });
    pearl.append(face);
    window.append(pearl);
    const name = document.createElement('span');
    name.className = 'clam-name';
    name.textContent = person.login;
    link.append(window, name);
    link.addEventListener('pointerenter', () => alignName(link));
    link.addEventListener('focus', () => alignName(link));
    bed.append(link);
    return { link, window, pearl, random, index, visible: false, arrived: false,
      hover: false, focus: false, engaged: false, sequence: [], hold: 0, boil: 0,
      nextBoil: 1, nextBreath: 0, bubble: -1, sand: -1 };
  });
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

  let art;
  try {
    const [spriteResponse, sheetResponse] = await Promise.all([
      fetch('assets/art/clams.svg?v=20261105j'), fetch('assets/art/clams.json?v=20261105j')
    ]);
    if (!spriteResponse.ok || !sheetResponse.ok) return;
    const [source, sheet] = await Promise.all([spriteResponse.text(), sheetResponse.json()]);
    const parsed = new DOMParser().parseFromString(source, 'image/svg+xml');
    if (parsed.querySelector('parsererror') || parsed.documentElement.localName !== 'svg') return;
    // Our own same-origin, committed sprite; parse XML rather than inserting HTML.
    const ids = new Set([...parsed.querySelectorAll('symbol')].map(node => node.id));
    if (!sheet.frames || !sheet.poses || !sheet.poses.rest?.length) return;
    const references = Object.values(sheet.frames).flatMap(frame => [frame.back, frame.front])
      .concat(sheet.rings, sheet.bubbles, sheet.sand);
    if (references.some(id => !ids.has(id))) return;
    const sprite = document.importNode(parsed.documentElement, true);
    sprite.setAttribute('aria-hidden', 'true');
    sprite.setAttribute('focusable', 'false');
    sprite.setAttribute('width', '0');
    sprite.setAttribute('height', '0');
    sprite.classList.add('clam-sprite');
    document.body.append(sprite);
    art = sheet;
  } catch { return; } // Avatars remain ordinary round links if either art file fails.

  const root = document.documentElement;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const canAnimate = () => root.dataset.motion !== 'off' && !reduced.matches;
  const visible = new Set();
  let timer = null;
  function plate(className) {
    const svg = svgElement('svg', { class: className, viewBox: art.viewBox, 'aria-hidden': 'true', focusable: 'false' });
    const use = svgElement('use');
    svg.append(use);
    return { svg, use };
  }
  function show(state, frameName) {
    const frame = art.frames[frameName];
    state.back.setAttribute('href', `#${frame.back}`);
    state.front.setAttribute('href', `#${frame.front}`);
    const [x, y, size] = frame.pearl;
    // The fixed sphere and camera give every exposure the same pearl position.
    state.pearl.style.left = `${(x - size / 2) / 120 * 100}%`;
    state.pearl.style.top = `${(y - size / 2) / 110 * 100}%`;
    state.pearl.style.width = `${size / 120 * 100}%`;
    state.pearl.style.height = `${size / 110 * 100}%`;
    state.pearl.style.visibility = frame.visible ? 'visible' : 'hidden';
    state.ring.setAttribute('href', `#${art.rings[state.boil % art.rings.length]}`);
  }
  function effect(state, kind) {
    const tick = state[kind];
    state[`${kind}Use`].setAttribute('visibility', tick < 0 ? 'hidden' : 'visible');
    if (tick >= 0) state[`${kind}Use`].setAttribute('href', `#${art[kind === 'bubble' ? 'bubbles' : 'sand'][Math.floor(tick / 2)]}`);
  }
  function nextBreath(state) { state.nextBreath = 48 + Math.floor(state.random() * 81); }
  function advance(state) {
    const exposure = state.sequence.shift();
    if (!exposure) return;
    const [frame, hold] = exposure;
    state.hold = hold;
    show(state, frame);
    if (state.entering && frame === 'wide-0') { state.sand = 0; effect(state, 'sand'); }
  }
  function sequence(state, exposures) {
    state.sequence = exposures;
    advance(state);
  }
  function enter(state) {
    state.arrived = true;
    state.entering = true;
    sequence(state, [['shut-0', 3 + state.index % 8 * 2 + Math.floor(state.random() * 3)],
      ['shut-1', 2], ['barely-0', 1], ['half-0', 1], ['wide-0', 2], ['settle-0', 2], ['rest-0', 2]]);
  }
  function interaction(state) {
    if (!canAnimate() || !state.visible) return;
    const engaged = state.hover || state.focus;
    if (engaged === state.engaged) return;
    state.engaged = engaged;
    state.arrived = true;
    state.entering = false;
    sequence(state, engaged
      ? [['half-0', 1], ['wide-0', 2]]
      : [['settle-0', 2], ['settle-1', 1], ['rest-0', 2]]);
  }
  for (const state of clams) {
    const back = plate('clam-back'), front = plate('clam-front');
    const ring = plate('clam-ring'), bubble = plate('clam-effect'), sand = plate('clam-effect');
    state.link.prepend(back.svg);
    state.window.after(front.svg, bubble.svg, sand.svg);
    ring.svg.setAttribute('preserveAspectRatio', 'none');
    state.pearl.append(ring.svg);
    Object.assign(state, { back: back.use, front: front.use, ring: ring.use, bubbleUse: bubble.use, sandUse: sand.use });
    state.link.classList.add('clam-drawn');
    state.boil = Math.floor(state.random() * 3);
    nextBreath(state);
    show(state, 'rest-0');
    effect(state, 'bubble'); effect(state, 'sand');
    state.link.addEventListener('pointerenter', event => {
      if (event.pointerType === 'mouse' || event.pointerType === 'pen') { state.hover = true; interaction(state); }
    });
    state.link.addEventListener('pointerleave', () => { state.hover = false; interaction(state); });
    state.link.addEventListener('focus', () => { state.focus = true; interaction(state); });
    state.link.addEventListener('blur', () => { state.focus = false; interaction(state); });
  }
  // One shared 8 fps clock. Held exposures produce the traditional "on twos" cadence;
  // no interpolation, CSS shell transforms, or per-clam timers are involved.
  function tick() {
    for (const state of visible) {
      for (const kind of ['bubble', 'sand']) {
        if (state[kind] >= 0) {
          state[kind] = state[kind] === 5 ? -1 : state[kind] + 1;
          effect(state, kind);
        }
      }
      const engaged = state.hover || state.focus;
      if (!engaged) state.nextBreath--;
      if (state.hold > 0 && --state.hold > 0) continue;
      if (state.sequence.length) { advance(state); continue; }
      state.entering = false;
      if (!engaged && state.nextBreath <= 0) {
        nextBreath(state);
        sequence(state, [['rest-0', 2], ['half-0', 2], ['barely-0', 2],
          ['half-1', 2], ['rest-1', 2], ['settle-0', 2], ['rest-2', 2]]);
        if (state.random() < .4) { state.bubble = 0; effect(state, 'bubble'); }
        continue;
      }
      if (--state.nextBoil <= 0) {
        state.boil++;
        const drawings = art.poses[engaged ? 'wide' : 'rest'];
        show(state, drawings[state.boil % drawings.length]);
        state.nextBoil = engaged ? 2 + Math.floor(state.random() * 3) : 4 + Math.floor(state.random() * 6);
      }
    }
  }
  function syncClock() {
    const running = canAnimate() && !document.hidden && visible.size > 0;
    if (!running && timer !== null) { clearInterval(timer); timer = null; }
    if (running && timer === null) timer = setInterval(tick, 125);
  }
  function motionChanged() {
    if (!canAnimate()) {
      for (const state of clams) {
        state.sequence = []; state.hold = 0; state.entering = false; state.engaged = false;
        state.bubble = state.sand = -1; state.boil = 0;
        show(state, 'rest-0'); effect(state, 'bubble'); effect(state, 'sand');
        if (state.visible) state.arrived = true;
      }
    } else {
      for (const state of visible) {
        if (state.hover || state.focus) interaction(state);
      }
    }
    syncClock();
  }
  function visibility(state, onScreen) {
    state.visible = onScreen;
    if (onScreen) {
      visible.add(state);
      if (!state.arrived) {
        if (canAnimate()) enter(state);
        else state.arrived = true;
      }
    } else visible.delete(state);
    syncClock();
  }
  if ('IntersectionObserver' in window) {
    const byLink = new Map(clams.map(state => [state.link, state]));
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) visibility(byLink.get(entry.target), entry.isIntersecting);
    }, { threshold: .1 });
    clams.forEach(state => observer.observe(state.link));
  } // Without viewport observation, keep the static open drawings.
  new MutationObserver(motionChanged).observe(root, { attributes: true, attributeFilter: ['data-motion'] });
  reduced.addEventListener('change', motionChanged);
  document.addEventListener('visibilitychange', syncClock);
  motionChanged();
})();
