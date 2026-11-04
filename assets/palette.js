// A small local perceptual tonal palette. OKLCH keeps the wallpaper hue through
// light and dark tones; chroma is reduced until each colour is inside sRGB.
const linear = x => x <= .04045 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4;
const gamma = x => x <= .0031308 ? 12.92 * x : 1.055 * x ** (1 / 2.4) - .055;
export function palette(seed, dark) {
  const rgb = /^#[0-9a-f]{6}$/i.test(seed) ? seed : '#00796b';
  const [r,g,b] = rgb.match(/\w\w/g).map(x => linear(parseInt(x,16) / 255));
  const l = Math.cbrt(.4122214708*r + .5363325363*g + .0514459929*b);
  const m = Math.cbrt(.2119034982*r + .6806995451*g + .1073969566*b);
  const s = Math.cbrt(.0883024619*r + .2817188376*g + .6299787005*b);
  const a = 1.9779984951*l - 2.428592205*m + .4505937099*s;
  const bb = .0259040371*l + .7827717662*m - .808675766*s;
  const hue = Math.atan2(bb,a);
  function tone(L,C=.035,h=hue) {
    let out;
    for (let i=0;i<50;i++) {
      const aa = C*Math.cos(h), bbb=C*Math.sin(h);
      const ll=(L+.3963377774*aa+.2158037573*bbb)**3;
      const mm=(L-.1055613458*aa-.0638541728*bbb)**3;
      const ss=(L-.0894841775*aa-1.291485548*bbb)**3;
      out=[4.0767416621*ll-3.3077115913*mm+.2309699292*ss,
        -1.2684380046*ll+2.6097574011*mm-.3413193965*ss,
        -.0041960863*ll-.7034186147*mm+1.707614701*ss];
      if(out.every(v=>v>=0 && v<=1)) break;
      C*=.88;
    }
    return '#'+out.map(v=>Math.round(gamma(Math.max(0,Math.min(1,v)))*255).toString(16).padStart(2,'0')).join('');
  }
  const t=(light,night,C=.035,h=hue)=>tone(dark?night:light,C,h);
  return {
    'primary':t(.43,.82,.12), 'on-primary':t(.99,.20,.018),
    'primary-container':t(.90,.30,.065), 'on-primary-container':t(.19,.94,.025),
    'secondary-container':t(.90,.31,.035), 'on-secondary-container':t(.20,.93,.025),
    'tertiary-container':t(.40,.78,.075,hue+1), 'on-tertiary-container':t(.99,.17,.015),
    'surface':t(.985,.16,.009), 'on-surface':t(.18,.95,.014),
    'on-surface-variant':t(.25,.89,.018),
    'surface-container-low':t(.96,.19,.012), 'surface-container':t(.94,.21,.014),
    'surface-container-high':t(.92,.24,.015), 'surface-container-highest':t(.90,.27,.016),
    'outline':t(.48,.65,.018), 'outline-variant':t(.75,.40,.018),
    'abyss':tone(dark?.12:.19,.027), 'deep-start':tone(dark?.22:.30,.035),
    'foam':tone(.97,.012)
  };
}
