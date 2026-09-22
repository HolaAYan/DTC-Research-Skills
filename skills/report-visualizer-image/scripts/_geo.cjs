// 正文区几何探针：量"正文区(副题下缘→页脚上缘)" 与内容占版比、居中、块间空隙、越界。
// 与 references/design-system.md §1.3 / §1.6 配套使用，验证：
//   fillPct ∈ [70, 80]，centerDelta ≈ 0，over=[]。
// 用法：node _geo.cjs <chrome.exe> <html1> [html2 ...]
// 注意：html 必须传绝对路径，且与 _sys.css 同目录；相对路径会被 Chrome 以盘符根解析为空白页。
const { spawn } = require('child_process');

const CHROME = process.argv[2];
const files = process.argv.slice(3);

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
    '--force-device-scale-factor=1', '--window-size=2000,2200',
    `--user-data-dir=${tmp}/rvgeo_${Date.now()}_${Math.floor(Math.random() * 1e6)}`,
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
  // 必须 encodeURI：路径含空格 / 中文时，CDP Page.navigate 会直接报 ERR_FILE_NOT_FOUND，
  // 页面变成 Chrome 错误页，此时所有量测值静默退化为默认值（fillPct=null）而不报错。
  const uri = encodeURI('file:///' + file.replace(/\\/g, '/'));
  await call('Page.navigate', { url: uri });
  for (let i = 0; i < 100; i++) {
    const st = await call('Runtime.evaluate', { expression: 'document.readyState', returnByValue: true });
    if (st.result.value === 'complete') break;
    await new Promise(r => setTimeout(r, 100));
  }
  await new Promise(r => setTimeout(r, 800));

  // 硬守卫：页面没真正加载时（路径错 / 编码错 / Chrome 错误页），下面所有量测都会
  // 静默退化成默认值。宁可显式失败，也不要给出「看起来正常」的空结论。
  const guard = await call('Runtime.evaluate', {
    expression: `(() => ({url: location.href.slice(0, 60),
      hasCanvas: !!document.querySelector('.canvas'),
      hasContent: !!document.querySelector('.content')}))()`,
    returnByValue: true,
  });
  const g = guard.result.value || {};
  if (g.url.startsWith('chrome-error') || !g.hasCanvas || !g.hasContent) {
    ws.close(); child.kill();
    return { file, error: 'PAGE_NOT_LOADED', url: g.url, hasCanvas: g.hasCanvas, hasContent: g.hasContent };
  }

  const expr = `(() => {
    // 画布尺寸从 .canvas 实测（兼容 4:3 = 1600x1200 与 3:4 = 1200x1600 等任意比例）
    const _cv=document.querySelector('.canvas');
    const _cr=_cv?_cv.getBoundingClientRect():{width:1600,height:1200};
    const W=Math.round(_cr.width)||1600, H=Math.round(_cr.height)||1200;
    const R=e=>{const r=e.getBoundingClientRect();return {t:+r.top.toFixed(1),b:+r.bottom.toFixed(1),l:+r.left.toFixed(1),ri:+r.right.toFixed(1),h:+r.height.toFixed(1)}};
    const sub=document.querySelector('.sub');
    const foot=document.querySelector('.foot');
    const bodyTop = sub?R(sub).b:0;
    const footTop = foot?R(foot).t:H;
    const bodyH = footTop-bodyTop;
    const content=document.querySelector('.content');
    const kids=[...(content?content.children:[])].filter(k=>{const s=getComputedStyle(k);const r=k.getBoundingClientRect();return s.display!=='none'&&r.width>4&&r.height>4;}).sort((a,b)=>a.getBoundingClientRect().top-b.getBoundingClientRect().top);
    let top=null,bottom=null;
    const blockGaps=[];
    let prevB=null;
    for(const k of kids){const r=k.getBoundingClientRect(); if(top===null||r.top<top)top=r.top; if(bottom===null||r.bottom>bottom)bottom=r.bottom; if(prevB!==null)blockGaps.push(Math.round(r.top-prevB)); prevB=r.bottom;}
    const over=[];
    for(const e of [...document.querySelectorAll('body *')]){
      const s=getComputedStyle(e); if(s.display==='none'||s.visibility==='hidden')continue;
      const r=e.getBoundingClientRect(); if(r.width<=0||r.height<=0)continue;
      if(r.right>W+2||r.bottom>H+2||r.left< -2||r.top< -2){
        over.push({cls:String(e.className||e.tagName).slice(0,34),txt:(e.textContent||'').trim().slice(0,26).replace(/\\s+/g,' '),l:Math.round(r.left),t:Math.round(r.top),ri:Math.round(r.right),b:Math.round(r.bottom)});
      }
    }
    const head=document.querySelector('.head');
    const headH = head?R(head).h:0;
    return {file:location.pathname.split('/').pop(),
      headH:+headH.toFixed(1), subBottom:+bodyTop.toFixed(1), footTop:+footTop.toFixed(1), bodyH:+bodyH.toFixed(1),
      fillTop: top===null?null:+top.toFixed(1), fillBottom: bottom===null?null:+bottom.toFixed(1),
      fillPct: top===null?null:+(((bottom-top)/bodyH)*100).toFixed(1),
      topGap: top===null?null:+((top-bodyTop)).toFixed(1), botGap: bottom===null?null:+((footTop-bottom)).toFixed(1),
      centerDelta: top===null?null:Math.round((top-bodyTop)-(footTop-bottom)),
      blockGaps, blockCount: kids.length,
      over: over.slice(0,12)};
  })()`;
  const out = await call('Runtime.evaluate', { expression: expr, returnByValue: true });
  ws.close(); child.kill();
  return out.result.value;
}

(async () => {
  for (const f of files) {
    try { console.log(JSON.stringify(await qa(f))); }
    catch (e) { console.log(JSON.stringify({ file: f, error: String(e) })); }
  }
})();
