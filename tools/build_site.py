# coding: utf-8
"""Render authored HTML chapters into a shared, dependency-free site shell."""
from pathlib import Path
from html import escape
import re

ROOT = Path(__file__).resolve().parent.parent
PAGES = [
    ('index.html', '01', 'Modem 基礎', '', ''),
    ('c-memory.html', '02', 'C 與記憶體', '讓每一個 byte，<br>都有清楚的<em>邊界</em>。', '從 pointer、生命週期到同步，建立閱讀 C logging 程式的基礎。'),
    ('binary-logging.html', '03', 'Binary Logging', '跟著一筆 log，<br>看懂<em>資料的旅程</em>。', '定義格式、解析 bytes、觀察 queue，再親手執行一個小型 logger。'),
    ('debugging.html', '04', 'Debugging 實作', '把問題縮小，<br>讓<em>證據</em>帶路。', '從重現、觀察到驗證，建立能應用在 Logging Service 的除錯方法。'),
]

def course_nav(current):
    return '<div class="chapter-nav" aria-label="學習主題">' + ''.join(
        f'<a href="{name}" class="{"current" if name == current else ""}"' +
        (' aria-current="page"' if name == current else '') + f'><span>{number}</span>{title}</a>'
        for name, number, title, _, _ in PAGES) + '</div>'

def toc(body):
    items = re.findall(r'<section id="([^"]+)".*?<h2>(.*?)</h2>', body, re.S)
    return '<nav aria-label="文章章節">' + ''.join(
        f'<a href="#{key}"><span>{i:02d}</span>{re.sub("<[^>]+>", "", title)}</a>'
        for i, (key, title) in enumerate(items, 1)) + '</nav>'

base = (ROOT / 'content/modem.html').read_text()
# Keep the first chapter's existing authored layout, with a real cross-page menu.
start = base.index('<div class="sidebar-label">')
end = base.index('<div class="sidebar-footer">')
old_nav = re.search(r'<nav.*?</nav>', base, re.S).group(0)
base = base[:start] + '<div class="sidebar-label">LEARNING PATH / 學習路徑</div>' + course_nav('index.html') + '<div class="sidebar-label toc-label">本篇章節</div>' + old_nav + base[end:]
base = base.replace('href="#"><span class="brand-icon">', 'href="index.html"><span class="brand-icon">')
base = base.replace('<body>', '<body data-chapter="modem-foundations">')
base = base.replace('<script src="assets/app.js" defer></script>', '<script src="assets/app.js" defer></script><link rel="icon" href="assets/favicon.svg" type="image/svg+xml">')
base = base.replace('<a href="https://beej.us/guide/bgc/html/index.html"><span>NEXT · C PROGRAMMING</span>', '<a href="c-memory.html"><span>NEXT · C PROGRAMMING</span>')
base = base.replace('接著補 C 與記憶體 ↗', '接著補 C 與記憶體 →')
(ROOT / 'index.html').write_text(base)

for index, (name, number, title, hero, description) in enumerate(PAGES[1:], 1):
    body = (ROOT / 'content' / name).read_text()
    header = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="{escape(description)}"><title>{title} · Engineering Fieldnotes</title><link rel="stylesheet" href="assets/style.css"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><script src="assets/app.js" defer></script><script src="assets/labs.js" defer></script></head>
<body data-chapter="{name[:-5]}"><a class="skip" href="#main">跳到主要內容</a><aside class="sidebar"><a class="brand" href="index.html"><span class="brand-icon">∿</span><span>FIELDNOTES<small>ENGINEERING KNOWLEDGE BASE</small></span></a><div class="sidebar-label">LEARNING PATH / 學習路徑</div>{course_nav(name)}<div class="sidebar-label toc-label">本篇章節</div>{toc(body)}<div class="sidebar-footer">公開知識 · 可重現練習<br><a href="https://github.com/peter0512lee/mediatek-career">View repository ↗</a></div></aside><div class="shell"><header class="topbar"><span>知識庫 <span class="slash">/</span> {title}</span><a href="#resources">公開參考資料 ↗</a></header><main id="main"><div class="eyebrow">CHAPTER {number} <span>LEARN BY BUILDING</span></div><h1>{hero}</h1><p class="lead">{description}</p><div class="meta"><span>入門 → 實作</span><span>約 25 分鐘閱讀</span><span>查核於 2026.11.08</span></div><div class="note"><strong>本篇學習方式</strong>先讀概念，再跑教學範例，最後用練習檢查理解。範例採 C11／host 環境；平台規則與公司的內部介面需另行確認。</div>'''
    previous = PAGES[index - 1]
    following = PAGES[index + 1] if index + 1 < len(PAGES) else PAGES[0]
    footer = f'''<div class="completion"><label><input type="checkbox" id="completed"> 我已理解本篇，並完成實作或自我檢查</label><span id="completion-status" role="status"></span></div><div class="page-links"><a href="{previous[0]}">← {previous[2]}</a><a href="{following[0]}">{following[2]} →</a></div><footer>ENGINEERING FIELDNOTES <span>個人學習筆記 · 公開資料整理 · 非 MediaTek 官方文件</span></footer></main></div></body></html>'''
    (ROOT / name).write_text(header + body + footer)
print('Rendered 4 chapters')
