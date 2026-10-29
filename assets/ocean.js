(() => {
  const ns = 'http://www.w3.org/2000/svg';
  document.querySelectorAll('.fish-card .icon').forEach(svg => {
    const body = document.createElementNS(ns, 'g');
    body.classList.add('fish-swimmer');
    [...svg.children].filter(el => !el.classList.contains('cookie')).forEach(el => body.append(el));
    svg.append(body);
  });
  // The existing mark is inserted by the colour script; grouping its fish keeps their eyes with them.
  const observer = new MutationObserver(() => {
    document.querySelectorAll('.woven-t > g:not([data-swim])').forEach(group => {
      group.dataset.swim = 'true';
      const paths = [...group.children];
      for (let i = 0; i < paths.length; i += 3) {
        const fish = document.createElementNS(ns, 'g');
        fish.classList.add('fish-swimmer');
        fish.style.animationDelay = `${-i / 3}s`;
        paths.slice(i, i + 3).forEach(path => fish.append(path));
        group.append(fish);
      }
    });
  });
  observer.observe(document.body, {childList:true,subtree:true});
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let choice = null;
  try { choice = localStorage.getItem('shoal-motion'); } catch {}
  const button = document.getElementById('motion-toggle');
  function apply() {
    const enabled = choice === null ? !reduced.matches : choice === 'on';
    document.documentElement.dataset.motion = enabled ? 'on' : 'off';
    button.setAttribute('aria-pressed', String(enabled));
    button.textContent = enabled ? 'Pause fish animations' : 'Play fish animations';
  }
  button.addEventListener('click', () => {
    choice = document.documentElement.dataset.motion === 'off' ? 'on' : 'off';
    try { localStorage.setItem('shoal-motion', choice); } catch {}
    apply();
  });
  reduced.addEventListener('change', () => { choice = null; apply(); });
  apply();
})();
