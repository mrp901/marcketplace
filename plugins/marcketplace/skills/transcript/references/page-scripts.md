# Page scripts

The three snippets the Flow runs inside the recording page, verbatim from the working method. Run each with `browser: run page script` against the tab recorded in Step 1. Never edit them; the selectors and timings are deliberate (see the end of this file).

## Probe (Step 3)

```js
let subs = document.querySelectorAll('[id^="sub-entry-"]').length;
if (!subs) {
  const b = [...document.querySelectorAll('button')].find(x =>
    /transcript/i.test((x.getAttribute('aria-label') || '') + ' ' + (x.innerText || '')));
  if (b) { b.click(); await new Promise(r => setTimeout(r, 2500)); }
  subs = document.querySelectorAll('[id^="sub-entry-"]').length;
}
let total = 0;
document.querySelectorAll('[aria-setsize]').forEach(e =>
  total = Math.max(total, +e.getAttribute('aria-setsize') || 0));
({ host: location.hostname, title: document.title.slice(0, 80), subs, total })
```

## Harvest (Step 4)

Time-boxed to stay under the 45-second execution cap, and resumable: state lives on `window.__STORE`.

```js
const sc = [...document.querySelectorAll('*')].find(el =>
  el.scrollHeight > el.clientHeight + 40 && el.clientHeight > 80 &&
  /auto|scroll/.test(getComputedStyle(el).overflowY) &&
  el.querySelector('[id^="sub-entry-"]'));
if (!sc) throw new Error('scroller not found');
const store = window.__STORE = window.__STORE || new Map();
const harvest = () => {
  document.querySelectorAll('div[role="group"][id^="entry-"]').forEach(g => {
    const n = +g.id.slice(6);
    if (store.has(n)) return;
    const sub = g.querySelector('[id^="sub-entry-"]');
    if (!sub) return;
    const txt = (sub.innerText || '').replace(/\s+/g, ' ').trim();
    if (!txt) return;
    store.set(n, { n, lab: (g.getAttribute('aria-label') || '').replace(/\s+/g, ' ').trim(), txt });
  });
};
let total = 0;
document.querySelectorAll('[aria-setsize]').forEach(e =>
  total = Math.max(total, +e.getAttribute('aria-setsize') || 0));
const step = Math.floor(sc.clientHeight * 0.65);
const deadline = Date.now() + 30000;
let pos = sc.scrollTop = 0;
await new Promise(r => setTimeout(r, 500));
harvest();
while (Date.now() < deadline && store.size < total) {
  const bottom = sc.scrollHeight - sc.clientHeight;
  if (pos >= bottom) { await new Promise(r => setTimeout(r, 600)); harvest(); break; }
  pos = Math.min(pos + step, bottom);
  sc.scrollTop = pos;
  await new Promise(r => setTimeout(r, 340));
  harvest();
}
const secs = s => {
  const h = /(\d+)\s*hour/.exec(s), m = /(\d+)\s*minute/.exec(s), x = /(\d+)\s*second/.exec(s);
  return (h ? +h[1] * 3600 : 0) + (m ? +m[1] * 60 : 0) + (x ? +x[1] : 0);
};
const mmss = t => `${Math.floor(t / 60)}:${String(t % 60).padStart(2, '0')}`;
const rows = [...store.values()].sort((a, b) => a.n - b.n).map(e => {
  const cut = e.lab.search(/\d+\s*(hour|minute|second)/);
  const sp = (cut > 0 ? e.lab.slice(0, cut) : '').trim();
  return { sp: sp || null, t: cut > -1 ? secs(e.lab) : null, txt: e.txt };
});
const blocks = [];
for (const r of rows) {
  const p = blocks[blocks.length - 1];
  if (p && p.sp === r.sp && r.sp) p.txt += ' ' + r.txt; else blocks.push({ ...r });
}
window.__TX = blocks.map(r =>
  r.sp ? `[${mmss(r.t || 0)}] **${r.sp}:** ${r.txt}` : `*${r.txt}*`).join('\n\n');
const sp = {};
blocks.forEach(b => { if (b.sp) sp[b.sp] = (sp[b.sp] || 0) + 1; });
({ captured: store.size, expected: total, chars: window.__TX.length,
   complete: store.size >= total, speakers: Object.keys(sp) })
```

## Resume check (Step 4, after a timeout error)

```js
({ store: window.__STORE ? window.__STORE.size : 0, tx: window.__TX ? window.__TX.length : 0 })
```

## Why the fragile-looking bits are that way

- Anchor selectors on `id="entry-N"` / `id="sub-entry-N"`, never on class names. Classes like `entryText-446` carry a per-build hash and change every release.
- Step by absolute scroll position. A "stop when no new entries appear" loop quits at ~20% because the list re-renders lazily.
- `aria-setsize` is the only reliable source of the true entry count.
