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

扫描但不修改：本地路径、密钥 / token、CLI 与抓取命令、Agent / Skill / prompt
关键词。命中不等于必须删（如正文正常提到"API 经济"），需人工判断。

用法：
    python filter_report.py report.md -o report.public.md
    python filter_report.py report.md                      # 输出到 stdout
    python filter_report.py report.md -o out.md --no-recover-sources
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


def render_sources_md(entries, label):
    lines = [f"# Sources（从结构化数据层抢救 · {len(entries)} 条）",
             "",
             f"> 由 filter_report.py 自 `{label}` 的结构化数据层抽取。",
             "> 保留 SRC ID / 名称 / 类型 / URL / access 日期，供 PDF 的 Sources 节使用；",
             "> YAML 语法与结构化字段一律不进入公开 PDF（SKILL.md §3.1 / §4 / §13）。",
             ""]
    for e in entries:
        bits = [f"- **{e['id']}**", e["name"] or "（名称未记录）"]
        if e["type"]:
            bits.append(f"— {e['type']}")
        if e["url"]:
            bits.append(f"— {e['url']}")
        if e["access"]:
            bits.append(f"· access {e['access']}")
        lines.append(" ".join(bits))
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


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="输入 Markdown")
    ap.add_argument("-o", "--output", default=None, help="输出 Markdown（默认 stdout）")
    ap.add_argument("--no-recover-sources", action="store_true",
                    help="不从被删的结构化数据层抢救 Source Registry")
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

    # 收尾清理：连续空行压缩、文末多余分隔线
    cleaned = []
    for ln in lines:
        if ln.strip() in ("", "---") and cleaned and cleaned[-1].strip() in ("", "---"):
            continue
        cleaned.append(ln.rstrip())
    while cleaned and cleaned[-1].strip() in ("", "---", "***"):
        cleaned.pop()
    out_text = "\n".join(cleaned) + "\n"

    sources = [] if args.no_recover_sources else recover_sources(removed_texts)
    side = None
    if sources:
        if args.output:
            out_p = Path(args.output)
            stem = re.sub(r"\.(?:md|markdown)$", "", out_p.name, flags=re.I)
            stem = re.sub(r"\.public$", "", stem)
            side = out_p.parent / (stem + ".sources.md")
        else:
            side = src.parent / (re.sub(r"\.public$", "", src.stem) + ".sources.md")
        side.write_text(render_sources_md(sources, src.name), encoding="utf-8")

    if args.output:
        Path(args.output).write_text(out_text, encoding="utf-8")
    else:
        sys.stdout.write(out_text)

    hits = scan(cleaned)

    if not args.quiet:
        err = sys.stderr
        print("", file=err)
        print("═" * 62, file=err)
        print(f"[filter_report] {src.name} → {args.output or 'stdout'}", file=err)
        print(f"  行数: {total} → {len(cleaned)}（删除 {total - len(cleaned)} 行）", file=err)
        print("  确定性删除：", file=err)
        for r in report or ["  （无命中）"]:
            print(("" if r.startswith("  ") else "  ") + r, file=err)
        if sources:
            print(f"  Source Registry 抢救: {len(sources)} 条 → {side.name}", file=err)
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
