#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTML → PNG 批量截图（Report Visualizer — Image 渲染器）

设计画布 1600×1200 逻辑像素，默认以 deviceScaleFactor=2 输出 3200×2400 PNG。
自动发现本机 Chrome / Edge / Chromium；也可 --browser 显式指定。

用法：
    python shot_to_png.py a.html b.html [c.html ...]
    python shot_to_png.py --outdir out --scale 2 a.html
    python shot_to_png.py --browser "C:/Program Files/.../chrome.exe" a.html

约定：
- 输出文件与 html 同名同目录（.png），或用 --outdir 指定目录。
- html 画布必须自带固定尺寸（.canvas 1600×1200），超出视口内容会被裁剪，请先保证无溢出。
纯标准库，无第三方依赖。
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

BROWSER_CANDIDATES = [
    # Windows
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    # macOS
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    # Linux
    "google-chrome", "chromium", "chromium-browser", "microsoft-edge",
]


def find_browser(explicit=None):
    if explicit:
        if os.path.exists(explicit):
            return explicit
        sys.exit(f"[shot_to_png] 指定浏览器不存在: {explicit}")
    for env in ("CHROME_PATH", "EDGE_PATH", "BROWSER_PATH"):
        p = os.environ.get(env)
        if p and os.path.exists(p):
            return p
    for cand in BROWSER_CANDIDATES:
        if os.path.isabs(cand):
            if os.path.exists(cand):
                return cand
        else:
            hit = shutil.which(cand)
            if hit:
                return hit
    sys.exit("[shot_to_png] 未找到 Chrome/Edge/Chromium，请用 --browser 指定路径")


def shoot(browser, html_path, out_path, width=1600, height=1200, scale=2, timeout=60):
    uri = "file:///" + os.path.abspath(html_path).replace("\\", "/")
    out_path = os.path.abspath(out_path)  # Edge/Chrome 需要绝对输出路径（相对路径在 Windows 会报 "系统找不到指定的路径"）
    tmpdir = tempfile.mkdtemp(prefix="rvshot_")
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--hide-scrollbars",
        f"--force-device-scale-factor={scale}",
        f"--window-size={width},{height}",
        f"--virtual-time-budget=5000",
        f"--user-data-dir={tmpdir}",
        f"--screenshot={out_path}",
        uri,
    ]
    if sys.platform.startswith("linux"):
        cmd.insert(2, "--no-sandbox")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        sys.exit(f"[shot_to_png] 截图超时: {html_path}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
        sys.exit(
            f"[shot_to_png] 截图失败: {html_path}\n"
            f"  browser: {browser}\n  stderr: {proc.stderr[:800]}"
        )
    size_kb = os.path.getsize(out_path) / 1024
    print(f"  ✓ {os.path.basename(out_path)}  ({int(size_kb)} KB, {width*scale}x{height*scale})")
    return out_path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("htmls", nargs="+", help="html 文件路径（一个或多个）")
    ap.add_argument("--browser", default=None, help="浏览器可执行文件路径")
    ap.add_argument("--scale", type=int, default=2)
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--height", type=int, default=1200)
    ap.add_argument("--outdir", default=None, help="输出目录（默认与 html 同目录）")
    ap.add_argument("--timeout", type=int, default=90)
    args = ap.parse_args()

    browser = find_browser(args.browser)
    print(f"[shot_to_png] browser: {browser}")
    for h in args.htmls:
        if not os.path.exists(h):
            print(f"  ! 跳过（不存在）: {h}")
            continue
        if args.outdir:
            os.makedirs(args.outdir, exist_ok=True)
            out = os.path.join(args.outdir, os.path.splitext(os.path.basename(h))[0] + ".png")
        else:
            out = os.path.splitext(h)[0] + ".png"
        shoot(browser, h, out, args.width, args.height, args.scale, args.timeout)
    print("[shot_to_png] done.")


if __name__ == "__main__":
    main()
