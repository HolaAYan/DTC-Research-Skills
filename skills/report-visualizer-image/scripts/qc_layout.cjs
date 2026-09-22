// Layout QA — 几何质检（可选，Node 22+ / 含全局 WebSocket）
// 检查每个 html 在 1600×1200 画布（4:3）内是否：元素越界(bad)、主内容侵入页脚(crowded)。
// 在无法目检 PNG 的无头环境下用；用法:
//   node qc_layout.cjs <chrome.exe> <绝对路径 html1> [html2 ...]
// 注意必须传绝对路径，相对路径会被 Chrome 以盘符根目录解析导致空白页误报。
// 输出 JSON 行：bad=[] 且 crowded 仅含 .canvas/.content 容器本身 → 布局通过。
// dist 字段给出纵向分布数据：topGap/botGap（内容区顶部/底部空隙）应相近且 ≤ ~140，
// last 应贴近 footTop（botGap 小），用于检查"页脚上方大片空白"。
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
  const portFile = require('os').tmpdir();
  const args = [CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--hide-scrollbars',
    '--force-device-scale-factor=1', '--window-size=1600,1200',
    `--user-data-dir=${portFile}/rvqa_${Date.now()}_${Math.floor(Math.random()*1e6)}`,
    '--remote-debugging-port=0', 'about:blank'];
  const child = spawn(CHROME, args.slice(1), { stdio: ['ignore', 'ignore', 'pipe'] });
  let wsUrl = null;
  child.stderr.on('data', (d) => {
    const m = String(d).match(/DevTools listening on (ws:\/\/[^\s]+)/);
    if (m && !wsUrl) wsUrl = m[1];
  });
  const deadline = Date.now() + 15000;
  while (!wsUrl && Date.now() < deadline) await new Promise(r => setTimeout(r, 50));
  if (!wsUrl) { child.kill(); return { file, error: 'cannot start chrome' }; }

  // 找到 page target（带重试，等 CDP 端口就绪；用 http 模块避免 fetch/代理差异）
  const http = require('http');
  const base = wsUrl.replace(/ws:\/\//, 'http://').replace(/\/devtools\/browser\/.*/, '');
  function getJson(p) {
    return new Promise((resolve) => {
      const req = http.get(base + p, { timeout: 2000 }, (res) => {
        let d = ''; res.on('data', (c) => d += c);
        res.on('end', () => { try { resolve(JSON.parse(d)); } catch (e) { resolve(null); } });
      });
      req.on('error', () => resolve(null)); req.on('timeout', () => { req.destroy(); resolve(null); });
    });
  }
  let list = null;
  for (let i = 0; i < 40; i++) {
    list = await getJson('/json/list');
    if (list && list.length) break;
    await new Promise(r => setTimeout(r, 150));
  }
  if (!list || !list.length) { child.kill(); return { file, error: 'CDP list unavailable' }; }
  const page = list.find(t => t.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.addEventListener('open', res); ws.addEventListener('error', rej); });
  const call = rpc(ws);

  const uri = encodeURI('file:///' + file.replace(/\\/g, '/'));
  await call('Page.navigate', { url: uri });
  // 等待加载完成
  for (let i = 0; i < 100; i++) {
    const st = await call('Runtime.evaluate', { expression: 'document.readyState', returnByValue: true });
    if (st.result.value === 'complete') break;
    await new Promise(r => setTimeout(r, 100));
  }
  await new Promise(r => setTimeout(r, 600));

  const expr = `(() => {
    const W=1600,H=1200;
    const docOverflowW = document.documentElement.scrollWidth > W+1;
    const docOverflowH = document.documentElement.scrollHeight > H+1;
    const bad=[];
    const els=[...document.querySelectorAll('body *')].filter(e=>{
      const s=getComputedStyle(e); if(s.display==='none'||s.visibility==='hidden')return false;
      const r=e.getBoundingClientRect(); return r.width>0&&r.height>0;
    });
    for(const e of els){
      const r=e.getBoundingClientRect();
      if(r.right>W+2||r.bottom>H+2||r.left< -2||r.top< -2){
        const inFoot=!!e.closest('.foot');
        bad.push({cls:(e.className&&String(e.className)).slice(0,40)||e.tagName, txt:(e.textContent||'').trim().slice(0,44).replace(/\\n/g,' '),
          l:Math.round(r.left),t:Math.round(r.top),ri:Math.round(r.right),b:Math.round(r.bottom),foot:inFoot});
      }
    }
    // 主内容(非foot)是否压到页脚区顶部(底部>900) —— 提示潜在重叠风险
    const footTop = document.querySelector('.foot')?document.querySelector('.foot').getBoundingClientRect().top:null;
    const crowded=[];
    if(footTop){
      for(const e of els){
        if(e.closest('.foot')||e.closest('.head'))continue;
        const r=e.getBoundingClientRect();
        if(r.bottom>footTop-4&&r.top<footTop-4&&r.height>6&&r.width>6){
          crowded.push({cls:(e.className&&String(e.className)).slice(0,40)||e.tagName,txt:(e.textContent||'').trim().slice(0,40).replace(/\\n/g,' '),b:Math.round(r.bottom)});
        }
      }
    }
    // 纵向分布：量内容区首/尾空隙，供检查是否均匀铺满（无大片底部空白）
    let dist=null;
    const contentEl=document.querySelector('.content');
    if(contentEl){
      const cb=contentEl.getBoundingClientRect();
      const kids=[...contentEl.children].filter(k=>{
        const s=getComputedStyle(k); const r=k.getBoundingClientRect();
        return s.display!=='none'&&s.visibility!=='hidden'&&r.height>6&&r.width>6;
      });
      if(kids.length){
        const rects=kids.map(k=>k.getBoundingClientRect()).sort((a,b)=>a.top-b.top);
        const first=Math.min(...rects.map(r=>r.top));
        const last=Math.max(...rects.map(r=>r.bottom));
        const gaps=[]; for(let i=1;i<rects.length;i++) gaps.push(Math.round(rects[i].top-rects[i-1].bottom));
        dist={cTop:Math.round(cb.top),cBottom:Math.round(cb.bottom),
          topGap:Math.round(first-cb.top),botGap:Math.round(cb.bottom-last),gaps,
          lastBottom:Math.round(last)};
      }
    }
    return {docOverflowW,docOverflowH,bad:bad.slice(0,12),crowded:crowded.slice(0,8),footTop:footTop?Math.round(footTop):null,dist};
  })()`;
  const out = await call('Runtime.evaluate', { expression: expr, returnByValue: true });
  ws.close(); child.kill();
  return { file, ...out.result.value };
}

(async () => {
  for (const f of files) {
    try { console.log(JSON.stringify(await qa(f))); }
    catch (e) { console.log(JSON.stringify({ file: f, error: String(e) })); }
  }
})();
