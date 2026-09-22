#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""filter_report.py — 公开分享内容过滤辅助（Report Visualizer — PDF）

对研究报告 Markdown 做**确定性**的内部内容剔除，并输出一份"内部痕迹扫描报告"
供人工复核。它只做机械可判定的删除，**不替代语义过滤**（AI/Skill/Agent 指令、
工具操作步骤等仍需按 SKILL.md §3.2 人工判断删除）。

确定性删除：
  1. 内部章节块：PART 3 / Structured Research Data / Final Quality Check / 自检 /
     质检清单 / 交付检查 等（从该标题起，到下一个同级或更高级标题为止；循环执行）
  2. fenced 结构化数据块：```yaml ```yml ```json（含 ~~~ 写法），以及首行以
     research: 开头的无标签围栏块
  3. Source Registry 抢救：被删除的 YAML 里若含 SRC 条目，抽取为
     `<输出名>.sources.md`（保留 ID / 名称 / URL / access 日期），供 PDF 的
     Sources 节使用 —— 来源属于必须保留的公开研究内容（SKILL.md §4 / §13）

确定性改写：
  4. 断链修复：删掉 PART 3 后，正文里"完整来源记录见 PART 3 的 Source Registry"
     这类指针会悬空。带来源语义的指针自动改写为公开版仍存在的目标（默认
     `文末「Sources — 完整来源登记」`）；不含来源语义的裸指针（如"本报告分
     PART 1 / PART 2 / PART 3"）无法机械判断，原样保留并列回报告由人工处理。
     用 --no-fix-part3-refs 关闭本条；用 --sources-ref 自定义目标文本。
  5. Sources 并回（--merge-sources）：把抢救出的来源登记以
     `## Sources — 完整来源登记` 小节追加到公开版 md 末尾，使 md 自包含。
     **默认关闭**：md 若只作为 PDF 的中间产物，PDF skill 会自行从 `.sources.md`
     生成 Sources 节，此时并回会造成重复。md 作为最终交付物直接分享时才开启。
  6. 输出恒以 LF 落盘（不随平台变 CRLF），保证同一输入在任何机器上产出字节一致。

扫描但不修改：本地路径、密钥 / token、CLI 与抓取命令、Agent / Skill / prompt
关键词。命中不等于必须删（如正文正常提到"API 经济"），需人工判断。

用法：
    python filter_report.py report.md -o report.public.md
    python filter_report.py report.md -o out.md --merge-sources    # md 自包含，可直接分享
    python filter_report.py report.md                      # 输出到 stdout
    python filter_report.py report.md -o out.md --no-recover-sources
    python filter_report.py report.md -o out.md --no-fix-part3-refs
    python filter_report.py report.md -o out.md --quiet
"""
import argparse
import re
import sys
from pathlib import Path

# ── 内部章节标题判定 ────────────────────────────────────────────────
INTERNAL_HEADING = re.compile(
    r"^\s{0,3}#{1,6}\s*(?:"
    r"PART\s*3\b|PART\s*III\b|第三部分|"
    r"Structured\s+Research\s+Data|结构化(?:研究)?数据|"
    r"Final\s+Quality\s+Check|Quality\s+Check|"
    r"交付(?:前)?自检|自检|质检清单|质量检查|内部(?:说明|备注)|"
    r"执行记录|工作日志|Generation\s+Notes?|Internal\s+Notes?"
    r")",
    re.IGNORECASE,
)
HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+\S")

FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})\s*([A-Za-z0-9_+-]*)\s*$")
STRUCT_LANGS = {"yaml", "yml", "json", "jsonc"}

# ── 断链修复：正文里指向已删除内部章节的引用 ────────────────────────
# 匹配"PART 3 [+ 可选来源后缀]"。后缀存在即认为该指针在讲来源，可直接改写。
REF_ANY = re.compile(
    r"[ \t]*(?:PART\s*(?:3|III)\b|第三部分)"
    r"(?:[ \t]*的)?[ \t]*"
    r"(?:Source\s*Registry\b|source_registry\b|"
    r"来源(?:登记|记录|条目|清单|总览|表)|"
    r"结构化(?:研究)?数据(?:层|块)?|Structured\s+Research\s+Data)?",
    re.IGNORECASE,
)
# 只匹配裸指针（无来源后缀），用于判断某次命中是否"语义不足"
REF_BARE_ONLY = re.compile(r"[ \t]*(?:PART\s*(?:3|III)\b|第三部分)[ \t]*", re.IGNORECASE)
# 同行 ±60 字符内出现下列词，视为该裸指针在讲来源 / 溯源
SRC_HINT = re.compile(
    r"(?:SRC[-\s]?\d|Source\s*Registry|source_registry|来源|信源|检索|溯源|可回溯|Traceab|结构化)",
    re.IGNORECASE,
)
# 来源编号占位符，改写时替换为登记表里的实际区间
SRC_PLACEHOLDER = re.compile(r"SRC[-\s]?0*[xX]{1,3}")
DEFAULT_SRC_REF = "文末「Sources — 完整来源登记」"
MERGED_HEADING = "## Sources — 完整来源登记"

# ── 扫描模式（命中需人工判断） ──────────────────────────────────────
SCAN_PATTERNS = [
    ("本地路径", re.compile(r"(?:[A-Za-z]:\\[\\\w\s.-]+|/(?:Users|home|mnt|Volumes)/[\w.-]+)")),
    ("密钥/凭据", re.compile(r"(?:sk-[A-Za-z0-9]{8,}|AKIA[0-9A-Z]{12,}|gh[pous]_[A-Za-z0-9]{20,}"
                          r"|Bearer\s+[A-Za-z0-9._-]{12,}|(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=])",
                          re.IGNORECASE)),
    ("CLI/抓取", re.compile(r"(?:^\s*\$\s+\w|curl\s+-|wget\s+|npm\s+(?:i|install|run)|pip\s+install"
                          r"|python\s+\S+\.py|node\s+\S+\.(?:js|cjs)|chrome\s+--headless|selenium"
                          r"|playwright|puppeteer|scrapy|BeautifulSoup|RPA\b|爬虫脚本)", re.IGNORECASE)),
    ("工具操作", re.compile(r"(?:快捷键|后台|抓取(?:步骤|脚本|命令)|API\s*(?:调用|参数|endpoint|接口|拉取)"
                          r"|接口地址|调试|控制台)", re.IGNORECASE)),
    ("Agent/Skill", re.compile(r"(?:SKILL\.md|skill\s*(?:指令|说明|实现)|prompt\s*(?:模板|指令)?"
                             r"|system\s+prompt|(?:让|请)\s*AI\s*(?:执行|生成|分析)"
                             r"|agent\s*(?:指令|工作流)|工作流说明|LLM|大模型指令)", re.IGNORECASE)),
    ("生成过程自指", re.compile(r"(?:本报告由|生成(?:过程|流程|方式)|信息来源方式|研究方法说明（内部）"
                              r"|通过\s*AI\s*生成)", re.IGNORECASE)),
]

SRC_ID = re.compile(r"SRC[-\s]?(\d+)", re.IGNORECASE)
KV = re.compile(
    r"([A-Za-z_][A-Za-z0-9_]*)\s*:\s*"
    r"(\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'|[^,}\n]+)"
)
NAME_KEYS = ("name", "source_name", "source", "title")
URL_KEYS = ("url", "link", "href")
ACCESS_KEYS = ("access_date", "accessed", "access", "date")
TYPE_KEYS = ("type", "category", "source_type")

# ── Sources 节渲染 ─────────────────────────────────────────────────
# 信源类型与释义取自 evidence-rules（公开报告里写"来源按可靠性分层"是标准表述）
TYPE_GLOSS = (
    ("First-party", "品牌官网与官方材料"),
    ("Platform", "第三方平台数据库"),
    ("Media", "权威与行业媒体"),
    ("Community", "社区"),
)
NUM_CN = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七", 8: "八"}


def read_text(path: Path) -> str:
    for enc in ("utf-8-sig", "utf-8", "gb18030", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    raise SystemExit(f"[filter_report] 无法解码文件: {path}")


def strip_internal_sections(lines, report):
    """循环删除内部章节块，返回 (保留行, 被删片段列表)。"""
    removed_text = []
    while True:
        cut = None
        for i, ln in enumerate(lines):
            if INTERNAL_HEADING.match(ln):
                cut = i
                break
        if cut is None:
            break
        level = len(HEADING.match(lines[cut]).group(1))
        end = len(lines)
        for j in range(cut + 1, len(lines)):
            m = HEADING.match(lines[j])
            if m and len(m.group(1)) <= level:
                end = j
                break
        title = lines[cut].strip()
        report.append(f"  删除内部章节: {title}  （{end - cut} 行）")
        removed_text.append("\n".join(lines[cut:end]))
        lines = lines[:cut] + lines[end:]
    return lines, removed_text


def strip_struct_blocks(lines, report):
    """删除 fenced yaml/json 块与 research: 根键的无标签块。返回 (保留行, 被删文本)。"""
    out, removed_text = [], []
    i = 0
    while i < len(lines):
        m = FENCE.match(lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        marker, lang = m.group(1), m.group(2).lower()
        # 找闭合围栏
        close = None
        for j in range(i + 1, len(lines)):
            if re.match(r"^\s{0,3}" + re.escape(marker[0]) + r"{3,}\s*$", lines[j]):
                close = j
                break
        if close is None:
            out.append(lines[i]); i += 1; continue
        body = lines[i + 1:close]
        first = next((b.strip() for b in body if b.strip()), "")
        is_struct = lang in STRUCT_LANGS or bool(re.match(r"^research\s*:", first))
        if is_struct:
            why = f"lang={lang or '无标签'}"
            if not lang:
                why += "，首行 research:"
            report.append(f"  删除结构化数据块: {why}（{close - i + 1} 行）")
            removed_text.append("\n".join(body))
        else:
            out.extend(lines[i:close + 1])
        i = close + 1
    return out, removed_text


def rewrite_internal_refs(lines, target, sources):
    """把正文里指向已删除内部章节的引用改写到公开版仍保留的目标。

    返回 (改写后的行, fixed, leftover)：
      fixed    —— [(行号, 改写处数, 行内容)]，供报告打印
      leftover —— [(行号, 行内容)]，裸指针且同行无来源语义，无法机械判断，需人工处理
    """
    out, fixed, leftover = [], [], []
    for idx, ln in enumerate(lines, 1):
        pieces, last, n = [], 0, 0
        for m in REF_ANY.finditer(ln):
            if REF_BARE_ONLY.fullmatch(m.group(0)):
                # 裸指针：仅当同行谈的是来源 / 溯源才改写，否则留给人工
                window = ln[max(0, m.start() - 60): m.end() + 60]
                if not SRC_HINT.search(window):
                    leftover.append((idx, ln.strip()))
                    continue
            pieces.append(ln[last:m.start()])
            pieces.append(target)
            last = m.end()
            n += 1
        if not n:
            out.append(ln)
            continue
        pieces.append(ln[last:])
        new = "".join(pieces)
        if sources:
            lo, hi = sources[0]["id"], sources[-1]["id"]
            new = SRC_PLACEHOLDER.sub(f"{lo} – {hi}", new)
        fixed.append((idx, n, new.strip()))
        out.append(new)
    return out, fixed, leftover


def recover_sources(removed_texts):
    """从被删除的内部文本中抢救 Source Registry（ID / 名称 / 类型 / URL / access 日期）。

    兼容两种写法：
      · 流式映射  - { id: SRC-005, name: "…", type: "First-party", url: "…", access_date: "…" }
      · 块式列表  - id: SRC-001\\n  name: …\\n  url: …
    只接受带 name 或 url 的条目，因此正文里的 `source: SRC-001` 引用不会被误当条目。
    """
    entries, seen = [], {}
    for text in removed_texts:
        # registry 取最后一个 sources:（结构化层里 `source:` 单数引用出现在更前面，会污染字段）
        m = None
        for cand in re.finditer(r"^[ \t]*sources\s*:", text, re.M):
            m = cand
        if m is None:
            m = re.search(r"^[ \t]*source\s*:", text, re.M)
        scope = text[m.start():] if m else text

        for mm in SRC_ID.finditer(scope):
            sid = "SRC-" + mm.group(1)
            line_end = scope.find("\n", mm.start())
            line = scope[mm.start(): line_end if line_end != -1 else len(scope)]
            if "{" in line or "}" in line:
                # 流式映射：一条一行，只在本行内解析
                chunk = line[: line.index("}") + 1] if "}" in line else line
            else:
                # 块式列表：向后扩到下一个 SRC id
                tail = scope[mm.start(): mm.start() + 700]
                nxt = SRC_ID.search(tail[5:])
                chunk = tail[: 5 + nxt.start()] if nxt else tail
            fields = {}
            for k, v in KV.findall(chunk):
                fields.setdefault(k.lower(), v.strip().strip("\"'").strip())
            pick = lambda keys: next((fields[k] for k in keys if fields.get(k)), "")
            name, url = pick(NAME_KEYS), pick(URL_KEYS)
            if not (name or url):
                continue
            atom = {"access": pick(ACCESS_KEYS), "type": pick(TYPE_KEYS)}
            if sid in seen:
                e = seen[sid]
                if not e["name"]: e["name"] = name
                if not e["url"]: e["url"] = url
                for k, v in atom.items():
                    if not e[k]: e[k] = v
                continue
            e = {"id": sid, "name": name, "url": url, **atom}
            seen[sid] = e
            entries.append(e)
    entries.sort(key=lambda e: int(re.sub(r"\D", "", e["id"]) or 0))
    return entries


def fmt_entry(e):
    bits = [f"- **{e['id']}**", e["name"] or "（名称未记录）"]
    if e["type"]:
        bits.append(f"— {e['type']}")
    if e["url"]:
        bits.append(f"— {e['url']}")
    if e["access"]:
        bits.append(f"· access {e['access']}")
    return " ".join(bits)


def render_sources_md(entries, label):
    """侧车文件（内部底稿，供 PDF 的 Sources 节与 URL 校验脚本使用）。"""
    lines = [f"# Sources（从结构化数据层抢救 · {len(entries)} 条）",
             "",
             f"> 由 filter_report.py 自 `{label}` 的结构化数据层抽取。",
             "> 保留 SRC ID / 名称 / 类型 / URL / access 日期，供 PDF 的 Sources 节使用；",
             "> YAML 语法与结构化字段一律不进入公开 PDF（SKILL.md §3.1 / §4 / §13）。",
             ""]
    lines += [fmt_entry(e) for e in entries]
    return "\n".join(lines) + "\n"


def render_sources_section(entries):
    """公开版正文里的 Sources 节：面向读者，不含工具名 / 流程 / 内部约定等自指。"""
    gloss = {k.lower(): v for k, v in TYPE_GLOSS}
    present = []
    for e in entries:
        t = (e["type"] or "").strip()
        if t and t.lower() not in [x.lower() for x in present]:
            present.append(t)
    # 已知类型按 TYPE_GLOSS 顺序排，未知类型保持出现顺序追加
    canon = [k for k, _ in TYPE_GLOSS if k.lower() in [t.lower() for t in present]]
    ordered = canon + [t for t in present if t.lower() not in [k.lower() for k in canon]]
    label = "/".join(f"{t}（{gloss[t.lower()]}）" if t.lower() in gloss else t for t in ordered)

    lines = ["---", "", MERGED_HEADING, "",
             "> 本报告全部数据与判断均可回溯到下列来源；编号与正文中的 `[SRC-0xx]` 标记一一对应。"]
    if ordered:
        n_cn = NUM_CN.get(len(ordered), str(len(ordered)))
        lines.append(f"> 共 {len(entries)} 条，按可靠性分为 {label}{n_cn}层，**一手优先**。")
    else:
        lines.append(f"> 共 {len(entries)} 条，**一手优先**。")
    dates = sorted({(e["access"] or "").strip() for e in entries if (e["access"] or "").strip()})
    if len(dates) == 1:
        lines.append(f"> 采集日期：{dates[0]}。")
    lines.append("")
    lines += [fmt_entry(e) for e in entries]
    return "\n".join(lines) + "\n"


def scan(lines):
    hits = {}
    for i, ln in enumerate(lines, 1):
        for name, pat in SCAN_PATTERNS:
            for m in pat.finditer(ln):
                snippet = ln.strip()
                if len(snippet) > 110:
                    snippet = snippet[:107] + "…"
                hits.setdefault(name, []).append((i, snippet))
    return hits


def write_text(path, text):
    """恒以 LF 落盘：Path.write_text 在 Windows 会把 \\n 转成 CRLF，导致同一份输入
    在不同平台产出不同字节，diff / 校验全部失真。"""
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def sidecar_path(output, src: Path):
    if output:
        out_p = Path(output)
        stem = re.sub(r"\.(?:md|markdown)$", "", out_p.name, flags=re.I)
        stem = re.sub(r"\.public$", "", stem)
        return out_p.parent / (stem + ".sources.md")
    return src.parent / (re.sub(r"\.public$", "", src.stem) + ".sources.md")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="输入 Markdown")
    ap.add_argument("-o", "--output", default=None, help="输出 Markdown（默认 stdout）")
    ap.add_argument("--no-recover-sources", action="store_true",
                    help="不从被删的结构化数据层抢救 Source Registry")
    ap.add_argument("--merge-sources", action="store_true",
                    help="把抢救出的来源登记以「%s」小节并回公开版末尾，使 md 自包含"
                         "（默认关闭：md 只作 PDF 中间产物时，Sources 节由 PDF skill 生成，"
                         "并回会重复）" % MERGED_HEADING)
    ap.add_argument("--no-fix-part3-refs", action="store_true",
                    help="不改写正文里指向已删除内部章节（PART 3）的引用")
    ap.add_argument("--sources-ref", default=DEFAULT_SRC_REF,
                    help="改写后的引用目标文本（默认：%s）" % DEFAULT_SRC_REF)
    ap.add_argument("--quiet", action="store_true", help="只输出结果，不打印报告")
    args = ap.parse_args()

    src = Path(args.input)
    text = read_text(src)
    lines = text.splitlines()
    total = len(lines)

    report, removed_texts = [], []
    lines, cut_text = strip_internal_sections(lines, report)
    removed_texts.extend(cut_text)
    lines, struct_text = strip_struct_blocks(lines, report)
    removed_texts.extend(struct_text)

    sources = [] if args.no_recover_sources else recover_sources(removed_texts)
    side = sidecar_path(args.output, src) if sources else None

    ref_fixed, ref_leftover = [], []
    if not args.no_fix_part3_refs:
        lines, ref_fixed, ref_leftover = rewrite_internal_refs(lines, args.sources_ref, sources)

    # 收尾清理：连续空行压缩、文末多余分隔线
    cleaned = []
    for ln in lines:
        if ln.strip() in ("", "---") and cleaned and cleaned[-1].strip() in ("", "---"):
            continue
        cleaned.append(ln.rstrip())
    while cleaned and cleaned[-1].strip() in ("", "---", "***"):
        cleaned.pop()
    out_text = "\n".join(cleaned) + "\n"

    merged = bool(args.merge_sources and sources)
    if merged:
        out_text = out_text.rstrip("\n") + "\n\n" + render_sources_section(sources)

    if side:
        write_text(side, render_sources_md(sources, src.name))
    if args.output:
        write_text(args.output, out_text)
    else:
        sys.stdout.write(out_text)

    hits = scan(out_text.splitlines())

    if not args.quiet:
        err = sys.stderr
        print("", file=err)
        print("═" * 62, file=err)
        print(f"[filter_report] {src.name} → {args.output or 'stdout'}", file=err)
        print(f"  行数: {total} → {len(out_text.splitlines())}（删除 {total - len(cleaned)} 行）", file=err)
        print("  确定性删除：", file=err)
        for r in report or ["  （无命中）"]:
            print(("" if r.startswith("  ") else "  ") + r, file=err)
        if sources:
            print(f"  Source Registry 抢救: {len(sources)} 条 → {side.name}", file=err)
        if ref_fixed:
            print(f"  断链修复（正文指向已删内部章节 → {args.sources_ref}）:", file=err)
            for ln, n, snip in ref_fixed:
                print(f"    L{ln}（{n} 处）: {snip[:110]}", file=err)
        if ref_leftover:
            print(f"  ⚠ 裸指针 {len(ref_leftover)} 处无法机械判断，需人工改链:", file=err)
            for ln, snip in ref_leftover[:6]:
                print(f"    L{ln}: {snip[:110]}", file=err)
            if len(ref_leftover) > 6:
                print(f"    … 另有 {len(ref_leftover) - 6} 处", file=err)
        if merged:
            print(f"  Sources 并回: {len(sources)} 条 → 公开版正文「{MERGED_HEADING}」", file=err)
        elif sources and not args.no_fix_part3_refs:
            print("  提示：正文引用已指向「%s」，但本次未并回该节。" % args.sources_ref, file=err)
            print("        md 作为最终交付物 → 加 --merge-sources；"
                  "md 仅作 PDF 中间产物 → PDF skill 会自行生成该节，无需并回。", file=err)
        if ref_fixed and not sources:
            print("  ⚠ 未抢救到来源登记，但正文引用已改写为「%s」。" % args.sources_ref, file=err)
            print("     该目标节目前不存在——请补充来源，或加 --no-fix-part3-refs 保留原文交人工处理。", file=err)
        print("  内部痕迹扫描（需人工判断，命中≠必删）：", file=err)
        if not hits:
            print("    （无命中）", file=err)
        for name, items in hits.items():
            print(f"    【{name}】{len(items)} 处", file=err)
            for ln, snip in items[:6]:
                print(f"      L{ln}: {snip}", file=err)
            if len(items) > 6:
                print(f"      … 另有 {len(items) - 6} 处", file=err)
        print("  下一步（不可跳过）：按 SKILL.md §3.2 做语义二次过滤，", file=err)
        print("  确认 AI/Skill/Agent 指令、工具与 API 操作步骤、本地路径、内部备注已全部清除。", file=err)
        print("═" * 62, file=err)

    return 0


if __name__ == "__main__":
    sys.exit(main())
