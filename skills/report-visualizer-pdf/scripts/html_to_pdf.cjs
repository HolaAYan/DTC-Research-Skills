#!/usr/bin/env node
/* html_to_pdf.cjs — HTML → A4 PDF 渲染器（Report Visualizer — PDF）
 *
 * 通过 Chrome/Edge DevTools Protocol 的 Page.printToPDF 渲染：
 *   · 真正的矢量文本 PDF（不是长图截图，不是网页缩放）
 *   · 页面尺寸与页边距由 CSS @page 决定（preferCSSPageSize）
 *   · 打印背景色（printBackground）
 *   · 注入逐页页脚：左 = <meta name="rv-footer-label">，右 = 第 X 页 / 共 Y 页
 *
 * 用法：
 *   node html_to_pdf.cjs <input.html> [output.pdf]
 *   node html_to_pdf.cjs report.html out.pdf --label "BrandA · 报告类型 · 2026-09"
 *   node html_to_pdf.cjs report.html --no-footer          # 不要页脚/页码
 *   node html_to_pdf.cjs report.html --simple             # 降级：CLI --print-to-pdf（无页码）
 *   node html_to_pdf.cjs report.html --browser "C:/Program Files/.../msedge.exe"
 *
 * 依赖：Node 22+（内置 fetch / WebSocket），本机 Chrome 或 Edge。零第三方依赖。
 */
'use strict';

const { spawn, execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const BROWSER_CANDIDATES = [
  // Windows
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  // macOS
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  // Linux
  'google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'microsoft-edge',
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function log(...a) { if (!process.env.RV_QUIET) console.log('[html_to_pdf]', ...a); }
function die(msg) { console.error('[html_to_pdf] ERROR ' + msg); process.exit(1); }

function findBrowser(explicit) {
  if (explicit) {
    if (fs.existsSync(explicit)) return explicit;
    die('指定的浏览器不存在: ' + explicit);
  }
  for (const env of ['CHROME_PATH', 'EDGE_PATH', 'BROWSER_PATH']) {
    const p = process.env[env];
    if (p && fs.existsSync(p)) return p;
  }
  for (const cand of BROWSER_CANDIDATES) {
    if (path.isAbsolute(cand)) { if (fs.existsSync(cand)) return cand; }
    else {
      try {
        const which = process.platform === 'win32' ? 'where' : 'which';
        const out = execFileSync(which, [cand], { stdio: ['ignore', 'pipe', 'ignore'] }).toString().split(/\r?\n/)[0].trim();
        if (out) return out;
      } catch (_) {}
    }
  }
  die('未找到 Chrome/Edge/Chromium，请用 --browser <path> 指定');
}

function fileUrl(p) {
  let u = 'file:///' + path.resolve(p).replace(/\\/g, '/');
  return u.replace(/ /g, '%20').replace(/#/g, '%23').replace(/\?/g, '%3F');
}

function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function killTree(child) {
  if (!child || child.killed) return;
  try {
    if (process.platform === 'win32') execFileSync('taskkill', ['/pid', String(child.pid), '/T', '/F'], { stdio: 'ignore' });
    else child.kill('SIGKILL');
  } catch (_) { try { child.kill(); } catch (__) {} }
}

function footerTemplate(label) {
  const left = esc(label || '');
  return '<div style="width:100%;padding:0 15mm;box-sizing:border-box;font-family:'
    + '\'Microsoft YaHei\',\'PingFang SC\',Arial,sans-serif;font-size:11px;color:#5c6470;'
    + 'display:flex;justify-content:space-between;align-items:center;">'
    + '<div style="flex:1 1 auto;border-top:.5pt solid #e4e6eb;padding-top:2mm;display:flex;'
    + 'justify-content:space-between;align-items:center;gap:10px;">'
    + '<span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">' + left + '</span>'
    + '<span style="white-space:nowrap;">第 <span class="pageNumber"></span> 页 / 共 <span class="totalPages"></span> 页</span>'
    + '</div></div>';
}

/* ---------- 降级模式：Chrome CLI 直接打印（无页码） ---------- */
function printSimple(browser, html, out) {
  const ud = fs.mkdtempSync(path.join(os.tmpdir(), 'rvpdf-cli-'));
  try {
    const args = ['--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
      '--hide-scrollbars', '--no-pdf-header-footer', '--user-data-dir=' + ud,
      '--print-to-pdf=' + path.resolve(out), fileUrl(html)];
    if (process.platform === 'linux') args.unshift('--no-sandbox');
    execFileSync(browser, args, { stdio: ['ignore', 'pipe', 'pipe'], timeout: 120000 });
  } finally { try { fs.rmSync(ud, { recursive: true, force: true }); } catch (_) {} }
  if (!fs.existsSync(out) || fs.statSync(out).size === 0) die('CLI 打印失败（--simple）');
  log('✓', path.basename(out), '(' + Math.round(fs.statSync(out).size / 1024) + ' KB, 无页码)');
}

/* ---------- 主流程：CDP Page.printToPDF ---------- */
async function printViaCdp(opts) {
  const { browser, html, out, footer, label, timeout, scale } = opts;
  const ud = fs.mkdtempSync(path.join(os.tmpdir(), 'rvpdf-'));
  let child = null, ws = null;
  try {
    // 1. 选一个可用调试端口
    let port = 0, base = 9100 + Math.floor(Math.random() * 700);
    for (let i = 0; i < 8; i++) { port = base + i; break; }

    const args = ['--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
      '--hide-scrollbars', '--remote-debugging-port=' + port, '--user-data-dir=' + ud, fileUrl(html)];
    if (process.platform === 'linux') args.unshift('--no-sandbox');
    child = spawn(browser, args, { stdio: 'ignore' });

    // 2. 等目标页出现
    let target = null;
    const deadline = Date.now() + timeout * 1000;
    while (Date.now() < deadline && !target) {
      try {
        const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
        target = list.find((t) => t.type === 'page' && t.webSocketDebuggerUrl
          && /^file:/.test(t.url || '') && decodeURIComponent(t.url).includes(path.basename(html)));
        if (!target) target = list.find((t) => t.type === 'page' && t.webSocketDebuggerUrl && /^file:/.test(t.url || ''));
      } catch (_) {}
      if (!target) await sleep(200);
    }
    if (!target) die('未能连接到浏览器调试目标（CDP）。可改用 --simple。');

    // 3. 连接并等待排版完成
    ws = new WebSocket(target.webSocketDebuggerUrl);
    let id = 0; const pending = new Map();
    const send = (method, params) => new Promise((res, rej) => {
      const mid = ++id; pending.set(mid, { res, rej });
      ws.send(JSON.stringify({ id: mid, method, params: params || {} }));
    });
    await new Promise((res, rej) => { ws.onopen = res; ws.onerror = () => rej(new Error('WebSocket 连接失败')); });
    ws.onmessage = (ev) => {
      let m; try { m = JSON.parse(ev.data); } catch (_) { return; }
      if (m.id && pending.has(m.id)) {
        const p = pending.get(m.id); pending.delete(m.id);
        m.error ? p.rej(new Error(JSON.stringify(m.error))) : p.res(m.result);
      }
    };
    await send('Page.enable');
    await send('Runtime.enable');

    const evalExpr = async (expr) => {
      const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
      return r && r.result ? r.result.value : undefined;
    };
    // 等 readyState=complete + 字体加载完成（不依赖 loadEventFired，避免错过事件）
    let ready = false;
    while (Date.now() < deadline && !ready) {
      try {
        ready = await evalExpr("(function(){return document.readyState==='complete'&&(!document.fonts||document.fonts.status==='loaded');})()");
      } catch (_) {}
      if (!ready) await sleep(150);
    }
    await sleep(350); // 布局稳定

    // 4. 读取页脚标识 / 作者
    const metaLabel = await evalExpr("(function(){var m=document.querySelector('meta[name=rv-footer-label]');return m?m.content:'';})()") || '';
    const author = await evalExpr("(function(){var m=document.querySelector('meta[name=rv-author]');return m?m.content:'';})()") || '';
    const useLabel = label || metaLabel;
    if (author) log('作者署名:', author);

    // 5. printToPDF（页面尺寸/页边距由 CSS @page 决定）
    const params = {
      printBackground: true,
      preferCSSPageSize: true,          // @page { size:A4 } 生效
      marginTop: 0, marginBottom: 0, marginLeft: 0, marginRight: 0, // 边距只在 CSS 里定义
      scale: scale || 1,
      displayHeaderFooter: !!footer,
      headerTemplate: '<div></div>',
      footerTemplate: footer ? footerTemplate(useLabel) : '<div></div>',
      transferMode: 'ReturnAsBase64',
    };
    const r = await send('Page.printToPDF', params);
    if (!r || !r.data) die('printToPDF 未返回数据');
    fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
    fs.writeFileSync(out, Buffer.from(r.data, 'base64'));
    const kb = Math.round(fs.statSync(out).size / 1024);
    log('✓', path.basename(out), '(' + kb + ' KB' + (footer ? ', 含页码页脚' : ', 无页脚') + ')');
  } finally {
    try { if (ws) ws.close(); } catch (_) {}
    killTree(child);
    await sleep(120);
    try { fs.rmSync(ud, { recursive: true, force: true }); } catch (_) {}
  }
}

function main() {
  const argv = process.argv.slice(2);
  const opts = { footer: true, timeout: 90, scale: 1, simple: false, label: null, browser: null, files: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--no-footer') opts.footer = false;
    else if (a === '--simple') opts.simple = true;
    else if (a === '--label') opts.label = argv[++i];
    else if (a === '--browser') opts.browser = argv[++i];
    else if (a === '--scale') opts.scale = parseFloat(argv[++i]);
    else if (a === '--timeout') opts.timeout = parseInt(argv[++i], 10);
    else if (a === '--quiet') process.env.RV_QUIET = '1';
    else if (a.startsWith('--')) die('未知参数: ' + a);
    else opts.files.push(a);
  }
  if (opts.files.length === 0) die('用法: node html_to_pdf.cjs <input.html> [output.pdf] [--no-footer] [--label "…"] [--simple] [--browser path]');

  const html = opts.files[0];
  if (!fs.existsSync(html)) die('输入 HTML 不存在: ' + html);
  const out = opts.files[1] || html.replace(/\.html?$/i, '') + '.pdf';
  const browser = findBrowser(opts.browser);
  log('browser:', browser);
  log('input :', path.resolve(html));
  log('output:', path.resolve(out));

  if (opts.simple) { printSimple(browser, html, out); return; }

  printViaCdp({ browser, html, out, footer: opts.footer, label: opts.label, timeout: opts.timeout, scale: opts.scale })
    .then(() => process.exit(0))
    .catch((e) => {
      console.error('[html_to_pdf] CDP 渲染失败:', e.message);
      console.error('[html_to_pdf] 尝试降级为 CLI 打印（无页码）…');
      try { printSimple(browser, html, out); process.exit(0); }
      catch (e2) { die('渲染失败: ' + e2.message); }
    });
}

main();
