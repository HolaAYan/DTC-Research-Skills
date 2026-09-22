// 来源页 URL 完整性校验：逐条比对渲染文本与 Source Registry，并检查是否被裁切（scrollHeight > clientHeight）。
// 用法：node _urlcheck.cjs <chrome.exe> <html1> [html2 ...] [--registry <sources.md|registry.json>]
//
// 通过线：条数 = Registry 条数、全部 textOk=true、urlClipped=false、urlMismatch=[]。
// Registry 两种形态都认：
//   · markdown 侧车表 —— `- **SRC-001** 名称 — First-party — https://… · access 2026-09-17`
//   · JSON —— 数组（或含数组的对象）中每项带 id/src_id/srcId 与 url 字段
// 不传 --registry 时退化为「只查裁切/折行」，无法验证文本逐字一致（此时打印提示，避免误判为通过）。
const { spawn } = require('child_process');
const fs = require('fs');
const CHROME = process.argv[2];
const rest = process.argv.slice(3);
let REGISTRY = null;
const files = [];
for (let i = 0; i < rest.length; i++) {
  if (rest[i] === '--registry') { REGISTRY = rest[++i]; continue; }
  files.push(rest[i]);
}

function loadRegistry(p) {
  if (!p) return null;
  const raw = fs.readFileSync(p, 'utf8');
  const map = new Map();
  if (p.toLowerCase().endsWith('.json')) {
    const data = JSON.parse(raw);
    const walk = (o) => {
      if (Array.isArray(o)) return o.forEach(walk);
      if (o && typeof o === 'object') {
        const id = o.id || o.src_id || o.srcId || o.SRC_ID;
        const url = o.url || o.URL || o.link;
        if (id && url) map.set(String(id).trim(), String(url).trim());
        for (const v of Object.values(o)) walk(v);
      }
    };
    walk(data);
    return map;
  }
  const re = /^-\s+\*\*(SRC-\d{3})\*\*\s+(.*?)\s+—\s+(\S+)\s+—\s+(\S+)\s+·\s+access\s+(\S+)\s*$/;
  for (const line of raw.split(/\r?\n/)) {
    const m = re.exec(line.trim());
    if (m) map.set(m[1], m[4]);
  }
  return map;
}

function rpc(ws) {
  let id = 0; const pending = new Map();
  ws.addEventListener('message', (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
  });
  return (method, params = {}) => new Promise((res, rej) => {
    const mid = ++id; pending.set(mid, (m) => (m.error ? rej(new Error(m.error.message)) : res(m.result)));
    ws.send(JSON.stringify({ id: mid, method, params }));
  });
}

async function qa(file) {
  const tmp = require('os').tmpdir();
  const child = spawn(CHROME, ['--headless=new', '--disable-gpu', '--no-first-run', '--hide-scrollbars',
    '--force-device-scale-factor=1', '--window-size=1600,1200',
    `--user-data-dir=${tmp}/rvurl_${Date.now()}_${Math.floor(Math.random() * 1e6)}`,
    '--remote-debugging-port=0', 'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });
  let wsUrl = null;
  child.stderr.on('data', (d) => {
    const m = String(d).match(/DevTools listening on (ws:\/\/[^\s]+)/);
    if (m && !wsUrl) wsUrl = m[1];
  });
  const deadline = Date.now() + 15000;
  while (!wsUrl && Date.now() < deadline) await new Promise(r => setTimeout(r, 50));
  if (!wsUrl) { child.kill(); return { file, error: 'cannot start chrome' }; }
  const http = require('http');
  const base = wsUrl.replace(/ws:\/\//, 'http://').replace(/\/devtools\/browser\/.*/, '');
  function getJson(p) {
    return new Promise((resolve) => {
      const req = http.get(base + p, { timeout: 2000 }, (res) => {
        let d = ''; res.on('data', (c) => d += c);
        res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve(null); } });
      });
      req.on('error', () => resolve(null)); req.on('timeout', () => { req.destroy(); resolve(null); });
    });
  }
  let list = null;
  for (let i = 0; i < 40; i++) { list = await getJson('/json/list'); if (list && list.length) break; await new Promise(r => setTimeout(r, 150)); }
  if (!list || !list.length) { child.kill(); return { file, error: 'CDP list unavailable' }; }
  const page = list.find(t => t.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.addEventListener('open', res); ws.addEventListener('error', rej); });
  const call = rpc(ws);
  await call('Page.navigate', { url: encodeURI('file:///' + file.replace(/\\/g, '/')) });
  for (let i = 0; i < 100; i++) {
    const st = await call('Runtime.evaluate', { expression: 'document.readyState', returnByValue: true });
    if (st.result.value === 'complete') break;
    await new Promise(r => setTimeout(r, 100));
  }
  await new Promise(r => setTimeout(r, 700));

  const expr = `(() => {
    const out=[];
    const ids=[...document.querySelectorAll('.se')].map(se=>{
      const sid=(se.querySelector('.sr .src')||{}).textContent||'';
      const nm=(se.querySelector('.nm')||{}).textContent||'';
      const ur=se.querySelector('.ur');
      const nmEl=se.querySelector('.nm');
      return {sid:sid.trim(), nm:nm,
        url:ur?ur.textContent:'',
        urlClipped: ur? ur.scrollHeight > ur.clientHeight + 1 : null,
        nmClipped: nmEl? nmEl.scrollWidth > nmEl.clientWidth + 1 : null,
        urlLines: ur? Math.round(ur.scrollHeight/ parseFloat(getComputedStyle(ur).lineHeight)) : null,
        urlW: ur? +ur.getBoundingClientRect().width.toFixed(0):null};
    });
    return {file:location.pathname.split('/').pop(), count:ids.length, items:ids};
  })()`;
  const out = await call('Runtime.evaluate', { expression: expr, returnByValue: true });
  ws.close(); child.kill();
  return out.result.value;
}

(async () => {
  const registry = loadRegistry(REGISTRY);
  if (REGISTRY && (!registry || !registry.size)) {
    console.log(JSON.stringify({ error: `registry 解析为空: ${REGISTRY}` }));
    process.exit(1);
  }
  const seen = new Set();
  let bad = 0;
  for (const f of files) {
    try {
      const r = await qa(f);
      if (r && r.items) {
        for (const it of r.items) {
          seen.add(it.sid);
          if (registry) {
            const want = registry.get(it.sid);
            it.registryUrl = want === undefined ? null : want;
            it.textOk = want === undefined ? null : (want === it.url);
            if (it.textOk === false || it.urlClipped) bad++;
          } else if (it.urlClipped) bad++;
        }
        const n = r.items.length;
        const ok = r.items.filter((i) => i.textOk === true).length;
        const mis = r.items.filter((i) => i.textOk === false).map((i) => i.sid);
        const clip = r.items.filter((i) => i.urlClipped).map((i) => i.sid);
        r.summary = {
          count: n,
          textOk: registry ? `${ok}/${n}` : 'SKIPPED(未传 --registry，仅查裁切)',
          urlMismatch: mis,
          urlClipped: clip,
        };
      }
      console.log(JSON.stringify(r));
    } catch (e) {
      console.log(JSON.stringify({ file: f, error: String(e) }));
      bad++;
    }
  }
  if (registry) {
    const unused = [...registry.keys()].filter((k) => !seen.has(k));
    console.log(JSON.stringify({
      registryTotal: registry.size, renderedTotal: seen.size,
      unusedInPages: unused, pass: bad === 0 && unused.length === 0,
    }));
  } else {
    console.log(JSON.stringify({
      note: '未传 --registry：本次只验证「无视觉裁切」，未验证文本与登记表逐字一致。',
    }));
  }
  process.exit(bad === 0 ? 0 : 1);
})();
