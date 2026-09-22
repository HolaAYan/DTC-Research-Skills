#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qc_pdf.py — PDF 输出质检（Report Visualizer — PDF）

对照 SKILL.md §17 清单做机器可判定的检查：

  A. 结构（纯标准库，始终可用）
     · 是否为合法 PDF（%PDF- 魔数）
     · 页数
     · 每页 MediaBox 是否 A4（595.28 × 841.89 pt ±3）且纵向
  B. 版式（需 pypdfium2 + pillow，缺失时自动跳过并提示）
     · 逐页墨迹覆盖率 → 近似空白页（<3%）/ 过满页（>92%）告警
     · 逐页内容包围盒（mm）→ 左右越界、顶部越界、侵入下边距告警
     · 页脚存在性 → 底部页脚带无墨迹即告警（页码 / 页脚缺失）
     · 逐页 PNG 导出到 <outdir>/（默认 pdf 同级 qc_png/）供目检
  C. 内容安全（--html 提供时）
     · 扫描最终 HTML 是否残留 Part 3、YAML 数据块、本地路径、密钥、CLI/抓取
       命令、Agent/Skill/prompt 等内部痕迹（命中需人工判断）

退出码：0 = 全部通过；1 = 有告警（建议处理）；2 = 硬错误（非法 PDF / 非 A4）

用法：
    python qc_pdf.py report.pdf
    python qc_pdf.py report.pdf --html report.html
    python qc_pdf.py report.pdf --no-footer          # 渲染时用了 --no-footer / --simple
    python qc_pdf.py report.pdf --no-render --quiet
"""
import argparse
import re
import sys
import zlib
from pathlib import Path

# A4
A4_W_PT, A4_H_PT = 595.28, 841.89
A4_W_MM, A4_H_MM = 210.0, 297.0
TOL_PT = 3.0

# 版式判定阈值（与 references/design-system.md §1 的页边距一致）
MARGIN_TOP_MM = 17.0
MARGIN_SIDE_MM = 15.0
MARGIN_BOTTOM_MM = 22.0
EDGE_TOL_MM = 1.5           # 允许的渲染取整误差
FOOTER_BAND_MM = 14.0       # 距页面底缘 14mm 内视为页脚带（Chrome 页脚实测落在 5–12mm）
INK_BLANK = 3.0
INK_FULL = 92.0

HTML_PATTERNS = [
    ("Part 3 残留", re.compile(r"PART\s*3\b|PART\s*III\b|第三部分|Structured\s+Research\s+Data", re.I)),
    ("YAML 数据块残留", re.compile(r"```\s*(?:yaml|yml|json)|research\s*:\s*$|evidence_type\s*:", re.I | re.M)),
    ("本地路径", re.compile(r"(?:[A-Za-z]:\\[\\\w\s.-]+|/(?:Users|home|mnt|Volumes)/[\w.-]+)")),
    ("密钥/凭据", re.compile(r"(?:sk-[A-Za-z0-9]{8,}|AKIA[0-9A-Z]{12,}|gh[pous]_[A-Za-z0-9]{20,}"
                           r"|Bearer\s+[A-Za-z0-9._-]{12,}|api[_-]?key\s*[:=])", re.I)),
    ("CLI/抓取", re.compile(r"(?:curl\s+-|wget\s+|npm\s+i(?:nstall)?\b|pip\s+install|chrome\s+--headless"
                          r"|selenium|playwright|puppeteer|scrap(?:e|ing))", re.I)),
    ("Agent/Skill", re.compile(r"(?:SKILL\.md|skill\s*(?:指令|说明|实现)|system\s+prompt|prompt\s*模板"
                             r"|(?:让|请)\s*AI\s*(?:执行|生成)|agent\s*(?:指令|工作流))", re.I)),
    ("工具名自指", re.compile(r"report-visualizer-\w+", re.I)),
]


# ────────────────────────── A. 结构检查 ──────────────────────────
def pdf_structure(path: Path):
    data = path.read_bytes()
    res = {"magic": data[:5] == b"%PDF-", "pages": 0, "mediabox": set(), "bytes": len(data)}
    if not res["magic"]:
        return res
    pages = re.findall(rb"/Type\s*/Page(?![s])", data)
    res["pages"] = len(pages)
    boxes = re.findall(rb"/MediaBox\s*\[([^\]]+)\]", data)
    if not boxes:  # 回退：解压流后再找
        for m in re.finditer(rb"stream\r?\n", data):
            s = m.end(); e = data.find(b"endstream", s)
            try:
                dec = zlib.decompress(data[s:e])
            except Exception:
                continue
            boxes += re.findall(rb"/MediaBox\s*\[([^\]]+)\]", dec)
            if not res["pages"]:
                res["pages"] = len(re.findall(rb"/Type\s*/Page(?![s])", dec))
    for b in boxes:
        nums = re.findall(rb"-?\d+(?:\.\d+)?", b)
        if len(nums) >= 4:
            w, h = float(nums[2]) - float(nums[0]), float(nums[3]) - float(nums[1])
            res["mediabox"].add((round(w, 2), round(h, 2)))
    return res


# ────────────────────────── B. 版式检查 ──────────────────────────
def page_metrics(im):
    """返回 (ink_pct, content_bbox_mm, flags)。

    正文包围盒**排除页脚带**，因此不会把横贯页面的页脚细线误判为正文越界。
    """
    w, h = im.size
    px = im.load()
    step = max(1, int(min(w, h) / 420))
    mmx = lambda v: v / w * A4_W_MM
    mmy = lambda v: v / h * A4_H_MM
    footer_top = A4_H_MM - FOOTER_BAND_MM

    total = ink = footer_ink = 0
    cx0 = cy0 = 10 ** 9
    cx1 = cy1 = -1
    for y in range(0, h, step):
        ymm = mmy(y)
        in_footer = ymm >= footer_top
        for x in range(0, w, step):
            total += 1
            if px[x, y] >= 245:
                continue
            ink += 1
            if in_footer:
                footer_ink += 1
                continue
            xmm = mmx(x)
            if xmm < cx0: cx0 = xmm
            if xmm > cx1: cx1 = xmm
            if ymm < cy0: cy0 = ymm
            if ymm > cy1: cy1 = ymm

    ink_pct = ink / max(1, total) * 100.0
    content = None if cx1 < 0 else (round(cx0, 1), round(cy0, 1), round(cx1, 1), round(cy1, 1))

    flags = []
    if ink_pct < INK_BLANK: flags.append("近似空白页")
    if ink_pct > INK_FULL: flags.append("页面过满")
    if content:
        if content[0] < MARGIN_SIDE_MM - EDGE_TOL_MM:
            flags.append(f"左侧越界({content[0]}mm)")
        if content[2] > A4_W_MM - MARGIN_SIDE_MM + EDGE_TOL_MM:
            flags.append(f"右侧越界({content[2]}mm)")
        if content[1] < MARGIN_TOP_MM - 2.5:
            flags.append(f"顶部越界({content[1]}mm)")
        if content[3] > A4_H_MM - MARGIN_BOTTOM_MM + 2.0:
            flags.append(f"底部越界({content[3]}mm)")
    if footer_ink == 0:
        flags.append("页脚缺失")
    return ink_pct, content, flags

def qc_layout(pdf_path: Path, outdir: Path, do_render=True):
    try:
        import pypdfium2 as pdfium
        from PIL import Image  # noqa: F401
    except Exception as e:
        print(f"  ! 跳过版式检查（缺少依赖: {e.__class__.__name__}）")
        print("    安装到独立虚拟环境后重跑：")
        print(r"      python -m venv .venv")
        print(r"      .venv/bin/python -m pip install pypdfium2 pillow")
        print(r"      （Windows: .venv\Scripts\python.exe -m pip install pypdfium2 pillow）")
        return []

    pdf = pdfium.PdfDocument(str(pdf_path))
    rows = []
    if do_render:
        outdir.mkdir(parents=True, exist_ok=True)
    for i in range(len(pdf)):
        page = pdf[i]
        pw, ph = page.get_size()
        rgb = page.render(scale=1.7).to_pil().convert("RGB")
        gray = rgb.convert("L")
        ink, bbox, flags = page_metrics(gray)
        if do_render:
            rgb.save(outdir / f"pg{i+1:02d}.png")
        rows.append({
            "page": i + 1, "size_pt": (round(pw, 1), round(ph, 1)),
            "ink": ink, "bbox": bbox, "flags": flags,
        })
    return rows


# ────────────────────────── C. 内容安全扫描 ──────────────────────────
def scan_html(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    # 去掉 style / script / 注释，减少误报
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<!--[\s\S]*?-->", " ", text)
    hits = {}
    for name, pat in HTML_PATTERNS:
        for m in pat.finditer(text):
            ln = text[:m.start()].count("\n") + 1
            snip = text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ").strip()
            hits.setdefault(name, []).append((ln, snip[:120]))
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", help="待质检 PDF")
    ap.add_argument("--html", default=None, help="对应的 A4 HTML（做内容安全扫描）")
    ap.add_argument("--outdir", default=None, help="渲染 PNG 输出目录（默认 <pdf 同级>/qc_png）")
    ap.add_argument("--no-render", action="store_true", help="不导出 PNG（仅度量）")
    ap.add_argument("--no-footer", action="store_true",
                    help="本 PDF 明确不带页脚（渲染时用了 --no-footer / --simple），跳过页脚检查")
    ap.add_argument("--quiet", action="store_true", help="精简输出")
    args = ap.parse_args()

    pdf = Path(args.pdf)
    if not pdf.exists():
        print(f"[qc_pdf] 文件不存在: {pdf}")
        return 2

    warns, errors = [], []
    print(f"[qc_pdf] {pdf}  ({pdf.stat().st_size/1024:.0f} KB)")

    # A. 结构
    st = pdf_structure(pdf)
    if not st["magic"]:
        print("  ✗ 不是合法 PDF（缺少 %PDF- 魔数）")
        return 2
    print(f"  页数: {st['pages']}")
    if not st["mediabox"]:
        warns.append("未能读到 MediaBox")
        print("  ! MediaBox 未读到")
    else:
        ok = False
        for (w, h) in sorted(st["mediabox"]):
            fit = abs(w - A4_W_PT) <= TOL_PT and abs(h - A4_H_PT) <= TOL_PT
            ok = ok or fit
            tag = "A4 纵向 ✓" if fit else ("A4 横向?" if abs(w - A4_H_PT) <= TOL_PT else "非 A4 ✗")
            print(f"  页面尺寸: {w} × {h} pt  →  {tag}")
        if not ok:
            errors.append("页面尺寸不是 A4")
    if st["pages"] == 0:
        errors.append("未解析到页面")

    # B. 版式
    outdir = Path(args.outdir) if args.outdir else pdf.parent / "qc_png"
    rows = qc_layout(pdf, outdir, do_render=not args.no_render)
    if rows:
        for r in rows:
            if args.no_footer:
                r["flags"] = [f for f in r["flags"] if f != "页脚缺失"]
            bbox = r["bbox"]
            b = f"内容 {bbox[1]:.0f}–{bbox[3]:.0f}mm" if bbox else "无内容"
            flag = ("  ⚠ " + " / ".join(r["flags"])) if r["flags"] else ""
            print(f"  pg{r['page']:>2} 墨迹 {r['ink']:5.1f}%  {b}{flag}")
        for r in rows:
            for f in r["flags"]:
                warns.append(f"pg{r['page']}: {f}")
        if not args.no_render:
            print(f"  渲染 PNG → {outdir}（请目检：首页层级 / 图表完整 / 卡片未被切开 / 页脚位置）")
        blanks = [r["page"] for r in rows if r["ink"] < INK_BLANK]
        if blanks:
            print(f"  ℹ 近似空白页: {blanks} — 若为「只承载收尾说明」的孤尾页，"
                  f"把收尾说明并入 Sources 区块或压缩最后一节（design-system §3.4）")

    # C. 内容安全
    if args.html:
        hp = Path(args.html)
        if not hp.exists():
            warns.append(f"--html 文件不存在: {hp}")
        else:
            hits = scan_html(hp)
            print(f"  内容安全扫描: {hp.name}")
            if not hits:
                print("    ✓ 未发现内部痕迹")
            else:
                for name, items in hits.items():
                    print(f"    ⚠ 【{name}】{len(items)} 处")
                    for ln, snip in items[:4]:
                        print(f"        L{ln}: {snip}")
                warns.extend(f"内容安全: {k}（{len(v)} 处）" for k, v in hits.items())

    # 汇总
    print("─" * 60)
    if errors:
        print("[qc_pdf] 结论: 存在必须修复的问题")
        for e in errors:
            print("   ✗ " + e)
    if warns:
        print("[qc_pdf] 告警（建议处理）:")
        for w in warns:
            print("   ⚠ " + w)
    if not errors and not warns:
        print("[qc_pdf] 结论: ✓ 全部检查通过")
    print("[qc_pdf] 提示: 脚本只覆盖可机检项；SKILL.md §17 的叙事层（首页 1 分钟可懂、"
          "核心结论最突出、无机械复制 Markdown）仍需人工目检。")
    return 2 if errors else (1 if warns else 0)


if __name__ == "__main__":
    sys.exit(main())
