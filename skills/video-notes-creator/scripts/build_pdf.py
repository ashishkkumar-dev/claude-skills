"""Build the notes PDF from the notes Markdown.

Usage: python build_pdf.py <notes.md> <notes.pdf>

Supports: # / ## / ### headings, paragraphs, - and 1. lists (indent for nesting),
**bold**, *italic*, `code`, pipe tables, and figures as ![caption](relative/path.png).
Links:
  [[n]](#ref-n)       citation that jumps to the resource row
  <a id="ref-n"></a>  anchor in the first cell of resource row n
  [2.4](#sec-2.4)     jump to the numbered heading "2.4 ..." (anchors are made automatically)
  [text](https://...) web link; bare https:// URLs are also clickable
Layout: a heading stays with its first figure or table; a figure stays with its caption.
"""
import re, sys, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, KeepTogether, CondPageBreak
from PIL import Image as PI

ss = getSampleStyleSheet()
body = ParagraphStyle('b', parent=ss['BodyText'], fontSize=9.5, leading=13)
cell = ParagraphStyle('c', parent=body, fontSize=8, leading=10)
cap = ParagraphStyle('cap', parent=body, fontName='Helvetica-Oblique', alignment=1, fontSize=8.5, leading=11, textColor=colors.HexColor('#444'))
h1, h2, h3 = ss['Title'], ss['Heading2'], ss['Heading3']
h2.keepWithNext = 1; h3.keepWithNext = 1
lead = ParagraphStyle('lead', parent=body, keepWithNext=1)
LC = '#1a5fb4'
W = A4[0] - 36*mm

def inl(t):
    t = re.sub(r'<a id="([\w.-]+)"></a>', '\x01\\1\x02', t)
    t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    t = re.sub('\x01([\\w.-]+)\x02', r'<a name="\1"/>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<!\*)\*(?!\s)(.+?)\*', r'<i>\1</i>', t)
    t = re.sub(r'`(.+?)`', r'<font face="Courier">\1</font>', t)
    t = re.sub(r'(?<![(\w/])(https?://[^\s<|)]+)', rf'<link href="\1" color="{LC}">\1</link>', t)
    t = re.sub(r'\[\[(\d+)\]\]\(#(ref-\d+)\)', rf'<a href="#\2" color="{LC}">[\1]</a>', t)
    t = re.sub(r'\[([^\]]+)\]\(#([\w.-]+)\)', rf'<a href="#\2" color="{LC}">\1</a>', t)
    t = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', rf'<link href="\2" color="{LC}">\1</link>', t)
    return t

def anchor(t):
    m = re.match(r'^(\d+(?:\.\d+)?)\.? ', t)
    return f'<a name="sec-{m.group(1)}"/>' if m else ''

def vis(x):
    x = re.sub(r'<a id="[^"]*"></a>', '', x)
    x = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', x)
    return len(x.strip())

def take_heading(story, styles):
    pre = []
    while story and (isinstance(story[-1], Spacer) or (isinstance(story[-1], Paragraph) and story[-1].style.name in styles)):
        pre.insert(0, story.pop())
    return pre

def build(src, out):
    """Convert the Markdown file src into the PDF out. Return the number of pages."""
    md = open(src, encoding='utf-8').read()
    story, title = to_story(md, os.path.dirname(os.path.abspath(src)))
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm, title=title)
    doc.build(story)
    return doc.page


def to_story(md, base):
    story = []; lines = md.split('\n'); i = 0; title = 'Study Notes'
    while i < len(lines):
        l = lines[i]
        mi = re.match(r'^!\[(.*)\]\((.*?)\)$', l)
        if mi:
            p = os.path.join(base, mi.group(2)); w, h = PI.open(p).size
            dw = W; dh = dw*h/w
            mx = 108*mm if p.endswith('.png') else 90*mm
            if dh > mx: dh = mx; dw = dh*w/h
            pre = take_heading(story, ('Heading2', 'Heading3', 'Title'))
            story.append(KeepTogether(pre + [Spacer(1, 4), Image(p, dw, dh), Spacer(1, 3), Paragraph(inl(mi.group(1)), cap), Spacer(1, 8)]))
            i += 1; continue
        if l.startswith('|'):
            rows = []; raw = []
            while i < len(lines) and lines[i].startswith('|'):
                if not re.match(r'^\|[-| :]+\|$', lines[i]):
                    cells = [x.strip() for x in lines[i].strip().strip('|').split('|')]
                    raw.append(cells); rows.append([Paragraph(inl(x), cell) for x in cells])
                i += 1
            nc = len(rows[0])
            wt = [min(max(max(vis(r[c]) for r in raw if c < len(r)), 3), 34) for c in range(nc)]
            wt = [max(w, sum(wt)/nc*0.45) for w in wt]
            t = Table(rows, colWidths=[W*w/sum(wt) for w in wt], repeatRows=1)
            t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.4, colors.grey), ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8e8f4')), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
            pre = take_heading(story, ('lead', 'Heading2', 'Heading3'))
            # A heading followed by one intro paragraph also stays with the table.
            if all(isinstance(x, Spacer) for x in pre) and story and isinstance(story[-1], Paragraph):
                k = len(story) - 2
                while k >= 0 and isinstance(story[k], Spacer): k -= 1
                if k >= 0 and isinstance(story[k], Paragraph) and story[k].style.name.startswith('Heading'):
                    pre = story[k:] + pre; del story[k:]
            long_table = len(rows) > 14
            story += ([CondPageBreak((100 if pre else 70)*mm)] + pre + [t] if long_table else [KeepTogether(pre + [t])]) + [Spacer(1, 8)]
            continue
        if l.startswith('# '):
            title = re.sub(r'[*`]', '', l[2:]); story.append(Paragraph(inl(l[2:]), h1))
        elif l.startswith('## '): story.append(Paragraph(anchor(l[3:]) + inl(l[3:]), h2))
        elif l.startswith('### '): story.append(Paragraph(anchor(l[4:]) + inl(l[4:]), h3))
        elif re.match(r'^\s*([-*]|\d+\.) ', l):
            m = re.match(r'^(\s*)([-*]|\d+\.) (.*)', l)
            b = '•' if m.group(2) in '-*' else m.group(2)
            story.append(Paragraph(inl(m.group(3)), ParagraphStyle('li', parent=body, leftIndent=12+len(m.group(1))*6, bulletIndent=2+len(m.group(1))*6), bulletText=b))
        elif l.strip():
            r = l.rstrip()
            story.append(Paragraph(inl(l), lead if l.startswith('**') and (r.endswith('**') or r.endswith(':')) else body))
        else: story.append(Spacer(1, 4))
        i += 1
    return story, title


if __name__ == '__main__':
    n = build(sys.argv[1], sys.argv[2])
    print('ok', sys.argv[2], n, 'pages')
