#!/usr/bin/env python3
"""图表着色语义审计 — 找出报告 HTML 里所有「答不出在告诉读者什么」的颜色。

用法:
    python audit_chart_colors.py <report.html>

背景（为什么需要这个脚本）:
    report-visualizer-html 的辅助色板 c2..c5 本质是证据分级语义色
    (--obs/--ok/--est/--inf 分别对应 OBSERVATION/FACT/ESTIMATE/INFERENCE 徽章)。
    一旦被当作「调色盘」随意使用 —— 给单条高亮、给时间序列某一根换色、
    给量纲不同的并列图形区分 —— 读者就会把「证据等级」误读成「数据分组」，
    或者以为某个变色项有特殊性质。这类问题浏览器不报错、视觉上也不难看，
    只能靠静态扫描 + 人工判断捕捉。

判定口径（脚本输出后由人逐条回答）:
    对每处非主题色，问一句「这个颜色在告诉读者什么？」
      · 答"这是竞品/这是本品牌"这类真实分组 → 合规，但必须同时存在色键 .ckey
      · 答不上来 / 只是"想突出一下" → 违规，改回主题色

退出码: 0 = 无明显问题; 1 = 发现需人工确认的非主题色着色点
"""
import re
import sys
import os

THEME_CLASSES = ('c1', 'c2', 'c3', 'c4', 'c5')
# 非主题色的其他着色途径
OTHER_PATTERNS = [
    (r'class="vcol alt"', '.vcol.alt（给某根柱单独换色）'),
    (r'--col:\s*var\(--(?!brand|accent)[a-z-]+\)', 'donut --col 覆盖（给某个环单独换色）'),
    (r'style="[^"]*background:\s*var\(--(?!brand|accent)[a-z-]+\)', '内联非主题背景色'),
]


def chart_title_before(html, pos):
    """返回 pos 之前最近的图表标题；找不到就返回所在 section id。"""
    heads = list(re.finditer(r'<h[23][^>]*class="[^"]*chart-title[^"]*"[^>]*>(.*?)</h[23]>',
                             html, re.S))
    title = None
    for h in heads:
        if h.start() < pos:
            title = re.sub(r'<[^>]+>', '', h.group(1)).strip()
        else:
            break
    if title:
        return title[:44]
    sec = '?'
    for s in re.finditer(r'<section id="([^"]+)"', html):
        if s.start() < pos:
            sec = s.group(1)
        else:
            break
    return 'section#%s' % sec


def audit(path):
    html = open(path, encoding='utf-8').read()
    problems = []

    print('文件: %s  (%.1f KB, %d 行)' % (os.path.basename(path),
                                         len(html.encode('utf-8')) / 1024,
                                         html.count('\n')))
    print()

    # 1. 色板类使用点
    print('=== 1. 色板类使用点（c1..c5）===')
    for cls in THEME_CLASSES:
        hits = list(re.finditer(r'class="[^"]*\b' + cls + r'\b[^"]*"', html))
        mark = '' if cls == 'c1' else ('   <-- 辅助色，需有真实分组理由' if hits else '')
        print('  .%s : %d 处%s' % (cls, len(hits), mark))
        if cls != 'c1':
            groups = {}
            for m in hits:
                t = chart_title_before(html, m.start())
                groups[t] = groups.get(t, 0) + 1
            for title, n in groups.items():
                print('        %d 处，位于图表「%s」' % (n, title))
                problems.append('%s ×%d @「%s」' % (cls, n, title))

    # 2. 其他非主题色途径
    print()
    print('=== 2. 其他非主题色途径 ===')
    for pat, desc in OTHER_PATTERNS:
        hits = list(re.finditer(pat, html))
        print('  %-46s %d 处' % (desc, len(hits)))
        for m in hits:
            start = max(0, m.start() - 160)
            print('        …%s' % re.sub(r'\s+', ' ', html[start:m.end() + 20]))
            problems.append(desc)

    # 3. 色键一致性
    print()
    print('=== 3. 色键 / 图例一致性 ===')
    n_ckey = len(re.findall(r'class="ckey"', html))
    n_legend = len(re.findall(r'class="legend"', html))
    print('  .ckey 图表色键     : %d 处' % n_ckey)
    print('  .legend 页头证据图例: %d 处  (应为 1；>1 说明类名被复用，会覆盖页头布局)'
          % n_legend)
    if n_legend != 1:
        problems.append('.legend 数量异常(%d)' % n_legend)

    has_aux = len(re.findall(r'class="[^"]*\bc[2-5]\b[^"]*"', html)) > 0
    if has_aux and n_ckey == 0:
        problems.append('用了辅助色但缺色键 .ckey')
        print('  [!] 存在辅助色着色，但页面没有 .ckey 色键 —— 读者无从知道颜色含义')
    elif has_aux:
        print('  OK 有辅助色且配了色键')

    # 4. ckey 内部色块与实际分组是否配对
    print()
    print('=== 4. 结论 ===')
    if problems:
        print('  需人工确认 %d 处：' % len(problems))
        for p in problems:
            print('    · %s' % p)
        print()
        print('  对每一处回答「这个颜色在告诉读者什么？」——答不上来的改回主题色。')
        return 1
    print('  未发现需人工确认的非主题色着色点。')
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(audit(sys.argv[1]))
