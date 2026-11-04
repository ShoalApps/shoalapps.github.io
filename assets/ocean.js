(() => {
  const root = document.documentElement;
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
