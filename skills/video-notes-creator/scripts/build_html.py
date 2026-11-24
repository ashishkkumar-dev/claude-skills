"""Build the notes web page from the notes Markdown.

Usage: python build_html.py <notes.md> <notes.html>

Supports: # / ## / ### headings, paragraphs, - and 1. lists (indent by 2 or more spaces to nest),
**bold**, *italic*, `code`, ``` code blocks (text after the fence is a label), pipe tables,
and figures as ![caption](figures/name.png).
Figures: two or more figure lines in a row (blank lines between them are fine) become one slider
with previous and next buttons, a counter, and thumbnails. Click any figure to open it full size.
Links:
  [[n]](#ref-n)       citation that jumps to the resource row
  <a id="ref-n"></a>  anchor in the first cell of resource row n
  [2.4](#sec-2.4)     jump to the numbered heading "2.4 ..." (anchors are made automatically)
  [text](https://...) web link; bare https:// URLs are also clickable
The page has a contents bar on the left. Images stay as files next to the page (paths as written).
Checks, printed as warnings: missing image files, links to anchors that do not exist, sentences over 20 words.
"""
import html, os, re, sys

MAX_WORDS = 20


def inl(t):
    """Inline Markdown to HTML."""
    codes = []
    t = re.sub(r'`([^`]+)`', lambda m: codes.append(m.group(1)) or f'\x03{len(codes) - 1}\x04', t)
    t = re.sub(r'<a id="([\w.-]+)"></a>', '\x01\\1\x02', t)
    t = html.escape(t, quote=False)
    t = re.sub('\x01([\\w.-]+)\x02', r'<a id="\1"></a>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<![*\w])\*(?![\s*])(.+?)(?<!\s)\*(?!\w)', r'<i>\1</i>', t)
    t = re.sub(r'(?<![(\w/="])(https?://[^\s<|)]+)', r'<a href="\1" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r'\[\[(\d+)\]\]\(#(ref-\d+)\)', r'<a class="cite" href="#\2">[\1]</a>', t)
    t = re.sub(r'\[([^\]]+)\]\(#([\w.-]+)\)', r'<a href="#\2">\1</a>', t)
    t = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    return re.sub('\x03(\\d+)\x04', lambda m: f'<code>{html.escape(codes[int(m.group(1))], quote=False)}</code>', t)


def anchor(t):
    """'2.4 Title' -> 'sec-2.4'; '8. Resources' -> 'sec-8'; else ''."""
    m = re.match(r'^(\d+(?:\.\d+)?)\.? ', t)
    return f'sec-{m.group(1)}' if m else ''


def plain(t):
    t = re.sub(r'<a id="[^"]*"></a>', '', t)
    t = re.sub(r'\[\[(\d+)\]\]\(#ref-\d+\)', r'[\1]', t)
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)
    return re.sub(r'[*`]', '', t)


def long_sentences(md):
    """Sentences over MAX_WORDS words, outside tables, figures, code, and bold labels."""
    out, code = [], False
    for line in md.split('\n'):
        if line.startswith('```'): code = not code; continue
        if code or line.startswith(('|', '![', '#')): continue
        line = re.sub(r'\*\*[^*]+\*\*', '', line)
        for s in re.split(r'(?<=[.!?])\s+', plain(line).strip(' -')):
            if len(re.findall(r"[\w$.'/-]+", s)) > MAX_WORDS: out.append(s.strip())
    return out


FIG = re.compile(r'^!\[(.*)\]\((.*?)\)(?:\{h=\d+\})?$')


def figure(cap, src, k):
    c = inl(cap)
    return (f'<figure class="fig" data-k="{k}"><img src="{html.escape(src)}" alt="{html.escape(plain(cap)[:120])}" loading="lazy">'
            f'<figcaption>{c}</figcaption></figure>')


def to_body(md, base):
    lines, i, parts, toc, figs, warn, title = md.split('\n'), 0, [], [], [], [], 'Study notes'
    k = 0
    while i < len(lines):
        l = lines[i]
        m = FIG.match(l)
        if m:
            group = []
            while i < len(lines):
                m2 = FIG.match(lines[i])
                if m2: group.append(m2.groups()); i += 1
                elif not lines[i].strip() and any(FIG.match(x) for x in lines[i + 1:i + 2]): i += 1
                else: break
            for cap, src in group:
                if not os.path.exists(os.path.join(base, src)): warn.append(f'missing image: {src}')
            if len(group) == 1:
                parts.append(figure(*group[0], k)); figs.append(1)
            else:
                items = ''.join(figure(c, s, k + j) for j, (c, s) in enumerate(group))
                thumbs = ''.join(f'<button class="thumb" aria-label="Figure {j + 1}"><img src="{html.escape(s)}" alt="" loading="lazy"></button>'
                                 for j, (c, s) in enumerate(group))
                parts.append(f'<div class="slider"><div class="track">{items}</div><div class="nav">'
                             f'<button class="prev" aria-label="Previous figure">&#9664;</button><span class="count"></span>'
                             f'<button class="next" aria-label="Next figure">&#9654;</button></div><div class="thumbs">{thumbs}</div></div>')
                figs.append(len(group))
            k += len(group)
            continue
        if l.startswith('```'):
            label, code = l[3:].strip(), []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'): code.append(lines[i]); i += 1
            i += 1
            lab = f'<div class="codelabel">{html.escape(label)}</div>' if label else ''
            parts.append(f'<div class="code">{lab}<pre><code>{html.escape(chr(10).join(code), quote=False)}</code></pre></div>')
            continue
        if l.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                if not re.match(r'^\|[-| :]+\|$', lines[i]):
                    rows.append([x.strip() for x in lines[i].strip().strip('|').split('|')])
                i += 1
            head = ''.join(f'<th>{inl(c)}</th>' for c in rows[0])
            body = ''.join('<tr>' + ''.join(f'<td>{inl(c)}</td>' for c in r) + '</tr>' for r in rows[1:])
            parts.append(f'<div class="tablewrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
            continue
        lm = re.match(r'^(\s*)([-*]|\d+\.) (.*)', l)
        if lm:
            stack = []          # (indent, tag)
            out = []
            while i < len(lines):
                lm = re.match(r'^(\s*)([-*]|\d+\.) (.*)', lines[i])
                if not lm: break
                ind, tag = len(lm.group(1)), 'ul' if lm.group(2) in '-*' else 'ol'
                while stack and ind < stack[-1][0]: out.append(f'</li></{stack.pop()[1]}>')
                if not stack or ind > stack[-1][0]: out.append(f'<{tag}>'); stack.append((ind, tag))
                else: out.append('</li>')
                out.append(f'<li>{inl(lm.group(3))}')
                i += 1
            while stack: out.append(f'</li></{stack.pop()[1]}>')
            parts.append(''.join(out))
            continue
        if l.startswith('# '):
            title = plain(l[2:]).strip(); parts.append(f'<h1>{inl(l[2:])}</h1>')
        elif l.startswith('## ') or l.startswith('### '):
            n = 2 if l.startswith('## ') else 3
            text = l[n + 1:]
            a = anchor(text) or 'h-' + re.sub(r'[^a-z0-9]+', '-', plain(text).lower()).strip('-')
            parts.append(f'<h{n} id="{a}">{inl(text)}</h{n}>')
            toc.append((n, a, plain(text).strip()))
        elif l.strip():
            parts.append(f'<p>{inl(l)}</p>')
        i += 1
    return title, '\n'.join(parts), toc, figs, warn


CSS = """
:root{--bg:#f7f7f5;--panel:#fff;--ink:#1f1f1f;--mute:#5f5f5f;--line:#e2e2de;--link:#1a5fb4;--accent:#1a5fb4;--code:#f1f1ee}
@media (prefers-color-scheme:dark){:root{--bg:#141414;--panel:#1e1e1e;--ink:#e9e9e9;--mute:#a3a3a3;--line:#333;--link:#7aa7ff;--accent:#7aa7ff;--code:#262626}}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 -apple-system,"Helvetica Neue",Arial,sans-serif}
a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}
#toc{position:fixed;top:0;left:0;bottom:0;width:270px;overflow:auto;padding:20px 14px;border-right:1px solid var(--line);background:var(--panel);font-size:13.5px}
#toc .t{font-weight:700;margin-bottom:10px;line-height:1.35}#toc a{display:block;padding:3px 6px;border-radius:6px;color:var(--ink)}
#toc a.l3{padding-left:20px;color:var(--mute)}#toc a.on{background:var(--code);color:var(--accent)}
main{margin-left:270px;padding:28px 40px 80px;max-width:1060px}
h1{font-size:30px;line-height:1.25;margin:4px 0 18px}h2{font-size:23px;margin:42px 0 10px;padding-top:6px;border-top:1px solid var(--line)}
h3{font-size:19px;margin:30px 0 8px}h2,h3{scroll-margin-top:12px}
p{margin:8px 0}ul,ol{margin:6px 0 10px;padding-left:24px}li{margin:3px 0}
code{background:var(--code);padding:1px 5px;border-radius:4px;font-size:.9em}
.code{background:var(--code);border:1px solid var(--line);border-radius:8px;margin:12px 0;overflow:auto}
.code pre{margin:0;padding:12px 14px;font-size:13px;line-height:1.45}.codelabel{font-size:12px;color:var(--mute);padding:6px 14px 0;font-weight:600}
.tablewrap{overflow-x:auto;margin:12px 0}table{border-collapse:collapse;font-size:14px;width:100%}
th,td{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}th{background:var(--code)}
figure{margin:18px 0;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px}
figure img{display:block;width:100%;height:auto;border-radius:6px;cursor:zoom-in;background:#fff}
figcaption{font-size:14px;color:var(--mute);margin-top:8px;font-style:italic}
.slider{margin:18px 0}.slider figure{margin:0}.slider .track figure{display:none}.slider .track figure.on{display:block}
.nav{display:flex;align-items:center;justify-content:center;gap:14px;margin:8px 0}
.nav button{font:inherit;font-size:18px;width:44px;height:36px;border-radius:8px;border:1px solid var(--line);background:var(--panel);color:var(--ink);cursor:pointer}
.nav .count{font-size:14px;color:var(--mute);min-width:60px;text-align:center}
.thumbs{display:flex;gap:8px;overflow-x:auto;padding:2px}.thumb{flex:0 0 120px;padding:0;border:2px solid transparent;border-radius:6px;background:none;cursor:pointer;opacity:.6}
.thumb img{display:block;width:100%;border-radius:4px}.thumb.on{border-color:var(--accent);opacity:1}
#lb{position:fixed;inset:0;background:#000;z-index:50;display:none;flex-direction:column}#lb.open{display:flex}
#lbbar{display:flex;gap:10px;align-items:center;padding:8px 12px;color:#ddd;background:#111;font-size:14px}
#lbbar button{font:inherit;background:#2a2a2a;color:#eee;border:1px solid #444;border-radius:7px;padding:5px 11px;cursor:pointer}
#lbbar .sp{flex:1}#lbview{flex:1;overflow:auto;display:flex;align-items:center;justify-content:center}
#lbimg{max-width:100%;max-height:100%;cursor:zoom-in;background:#fff}#lbview.full{display:block}#lbview.full #lbimg{max-width:none;max-height:none;cursor:zoom-out}
#lbcap{color:#bbb;font-size:14px;padding:8px 14px;background:#111}
@media (max-width:900px){#toc{position:static;width:auto;border-right:0;border-bottom:1px solid var(--line);max-height:40vh}main{margin-left:0;padding:20px 16px 60px}}
@media print{#toc,.nav,.thumbs,#lb{display:none}main{margin:0}.slider .track figure{display:block;margin-bottom:12px}}
"""

JS = """
const figs=[...document.querySelectorAll('main figure')];
document.querySelectorAll('.slider').forEach(s=>{
  const f=[...s.querySelectorAll('.track figure')],t=[...s.querySelectorAll('.thumb')],c=s.querySelector('.count');let k=0;
  const show=i=>{k=(i+f.length)%f.length;f.forEach((x,j)=>x.classList.toggle('on',j===k));t.forEach((x,j)=>x.classList.toggle('on',j===k));c.textContent=(k+1)+' / '+f.length};
  s.querySelector('.prev').onclick=()=>show(k-1);s.querySelector('.next').onclick=()=>show(k+1);
  t.forEach((x,j)=>x.onclick=()=>show(j));s.show=show;show(0);
  s.tabIndex=0;s.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')show(k-1);if(e.key==='ArrowRight')show(k+1)});
});
const lb=document.getElementById('lb'),view=document.getElementById('lbview'),img=document.getElementById('lbimg');let cur=-1;
const open=i=>{if(i<0||i>=figs.length)return;cur=i;const f=figs[i];img.src=f.querySelector('img').src;
  document.getElementById('lbcap').innerHTML=f.querySelector('figcaption').innerHTML;document.getElementById('lbn').textContent='Figure '+(i+1)+' of '+figs.length;
  view.classList.remove('full');lb.classList.add('open');const s=f.closest('.slider');if(s)s.show([...s.querySelectorAll('.track figure')].indexOf(f))};
const close=()=>{lb.classList.remove('open');cur=-1};
figs.forEach((f,i)=>f.querySelector('img').onclick=()=>open(i));
img.onclick=e=>{const z=!view.classList.contains('full');const rx=e.offsetX/img.clientWidth,ry=e.offsetY/img.clientHeight;view.classList.toggle('full',z);
  if(z){view.scrollLeft=rx*img.naturalWidth-view.clientWidth/2;view.scrollTop=ry*img.naturalHeight-view.clientHeight/2}};
document.getElementById('lbp').onclick=()=>open(cur-1);document.getElementById('lbx').onclick=()=>open(cur+1);document.getElementById('lbc').onclick=close;
document.addEventListener('keydown',e=>{if(cur<0)return;if(e.key==='Escape')close();if(e.key==='ArrowLeft')open(cur-1);if(e.key==='ArrowRight')open(cur+1)});
const links=[...document.querySelectorAll('#toc a')],heads=links.map(a=>document.getElementById(a.getAttribute('href').slice(1)));
const mark=()=>{let k=0;heads.forEach((h,i)=>{if(h&&h.getBoundingClientRect().top<120)k=i});links.forEach((a,i)=>a.classList.toggle('on',i===k))};
document.addEventListener('scroll',mark,{passive:true});mark();
"""


def build(src, out):
    """Convert the Markdown file src into the web page out. Return the list of warnings."""
    md = open(src, encoding='utf-8').read()
    base = os.path.dirname(os.path.abspath(src))
    title, body, toc, figs, warn = to_body(md, base)
    ids = set(re.findall(r'id="([^"]+)"', body))
    for t in sorted(set(re.findall(r'href="#([^"]+)"', body)) - ids): warn.append(f'link to a missing anchor: #{t}')
    for s in long_sentences(md): warn.append(f'sentence over {MAX_WORDS} words: {s[:90]}')
    nav = ''.join(f'<a class="l{n}" href="#{a}">{html.escape(t)}</a>' for n, a, t in toc)
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{html.escape(title)}</title><style>{CSS}</style></head><body>'
            f'<nav id="toc"><div class="t">{html.escape(title)}</div>{nav}</nav><main>{body}</main>'
            f'<div id="lb"><div id="lbbar"><b id="lbn"></b><span class="sp"></span><button id="lbp">&#9664; Previous</button>'
            f'<button id="lbx">Next &#9654;</button><button id="lbc">Close (Esc)</button></div>'
            f'<div id="lbview"><img id="lbimg" alt=""></div><div id="lbcap"></div></div><script>{JS}</script></body></html>')
    open(out, 'w', encoding='utf-8').write(page)
    build.stats = dict(sections=len(toc), figures=sum(figs), sliders=sum(1 for n in figs if n > 1))
    return warn


if __name__ == '__main__':
    w = build(sys.argv[1], sys.argv[2])
    s = build.stats
    print(f"ok {sys.argv[2]}: {s['sections']} sections, {s['figures']} figures ({s['sliders']} sliders), {len(w)} warnings")
    for x in w: print('  warning:', x)
