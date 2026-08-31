#!/usr/bin/env python3
"""Genereert de site in docs/ uit data/ en kaarten/.
Gebruik: python3 tools/build.py
Vereist: python3, markdown, pyyaml (pip install markdown pyyaml)
"""
import json, os, re, html, glob, shutil
from collections import defaultdict
import markdown, yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(ROOT, *p)
OUT = D('docs')
ARSENAAL = 'https://lucopdb-cpu.github.io/Theatre-of-the-Oppressed/'

sporen = json.load(open(D('data/sporen.json')))
groepen = json.load(open(D('data/projectgroepen.json')))
projecten = json.load(open(D('data/projecten.json')))
route = json.load(open(D('data/route.json')))
organisatie = json.load(open(D('data/organisatie.json')))
media = json.load(open(D('data/media.json')))
site = json.load(open(D('data/site.json')))

G = {g['id']: g for g in groepen}
S = {s['id']: s for s in sporen}
items_by_group = defaultdict(list)
for p in projecten:
    items_by_group[p['groep']].append(p)
media_by_group = {k: defaultdict(list) for k in media}
for k, lst in media.items():
    for m in lst:
        media_by_group[k][m['groep']].append(m)

# kaarten inlezen
kaarten = {}
for f in sorted(glob.glob(D('kaarten/*.md'))):
    if os.path.basename(f).startswith('_'):
        continue
    txt = open(f, encoding='utf-8').read()
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', txt, re.S)
    if not m:
        continue
    fm = yaml.safe_load(m.group(1)) or {}
    kaarten[fm.get('id', os.path.basename(f)[:-3])] = {'fm': fm, 'body': m.group(2)}

Y0, Y1 = site['jaar_van'], site['jaar_tot']
NY = Y1 - Y0 + 1
esc = html.escape

CSS = open(D('tools/site.css'), encoding='utf-8').read()

def page(title, body, depth=0, desc=''):
    rel = '../' * depth
    nav = ''.join(f'<a href="{rel}{h}">{t}</a>' for h, t in [('index.html', 'Tijdlijn'), ('route.html', 'Maak kennis'), ('thema.html', "Thema's"), ('organisatie.html', 'De organisatie'), ('alles.html', 'Alle activiteiten'), ('bronnen.html', 'Bronnen'), ('over.html', 'Over')])
    return f'''<!doctype html>
<html lang="nl" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Formaat 1999–2025</title>
<meta name="description" content="{esc(desc or site['omschrijving'])}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{CSS}</style>
</head>
<body>
<header class="top">
  <div class="wrap topbar">
    <a class="brand" href="{rel}index.html">Formaat <span>1999–2025</span></a>
    <nav>{nav}<a class="ext" href="{ARSENAAL}">Arsenaal van de joker ↗</a></nav>
  </div>
</header>
{body}
<footer><div class="wrap">
<p>{esc(site['colofon'])}</p>
<p>Licentie: {esc(site['licentie'])}. Bronmateriaal: {esc(site['bronnen_noot'])}</p>
<p class="mono">Gegenereerd uit <code>data/</code> en <code>kaarten/</code> · <a href="{esc(site['repo'])}">broncode en correcties</a></p>
</div></footer>
</body>
</html>'''

def bar(g, depth=0):
    c0 = max(1, g['van'] - Y0 + 1)
    c1 = min(NY + 1, g['tot'] - Y0 + 2)
    if c1 <= c0:
        c1 = c0 + 1
    href = f'{"../"*depth}kaarten/{g["id"]}.html' if g['id'] in kaarten else f'{"../"*depth}alles.html#{g["id"]}'
    cls = 'bar' + ('' if g['id'] in kaarten else ' stub')
    return f'<a class="{cls}" style="grid-column:{c0}/{c1}" href="{href}" title="{esc(g["naam"])} · {g["van"]}–{g["tot"]} · {g["n"]} activiteiten" data-n="{g["n"]}">{esc(g["titel_kort"])}</a>'

def tijdlijn(depth=0):
    years = ''.join(f'<span>{y}</span>' for y in range(Y0, Y1 + 1))
    band = fasenband(depth)
    rows = ''
    for s in sporen:
        gs = sorted([g for g in groepen if g['spoor'] == s['id']], key=lambda g: (g['van'], -g['n']))
        if not gs:
            continue
        rows += f'<div class="track-label"><b>{esc(s["naam"])}</b><small>{esc(s["sub"])}</small></div>'
        rows += f'<div class="track" style="--c:{s["kleur"]}">' + ''.join(bar(g, depth) for g in gs) + '</div>'
    return f'''<div class="tl"><div class="tl-inner" style="--ny:{NY}">
<div></div><div class="tl-years">{years}</div>{band}{rows}
<div class="tl-note">Elke balk is een projectlijn; de lengte is de looptijd, het cijfer het aantal activiteiten in de inventaris. Lichte balken hebben nog geen eigen kaart en verwijzen naar de index.</div>
</div></div>'''

def fasenband(depth=0, link=True):
    cells = ''
    for f in organisatie['fasen']:
        c0 = max(1, f['van'] - Y0 + 1)
        c1 = min(NY + 1, f['tot'] - Y0 + 1)
        if c1 <= c0:
            c1 = c0 + 1
        href = f'{"../"*depth}organisatie.html#{f["id"]}'
        cells += f'<a class="fase" style="grid-column:{c0}/{c1}" href="{href}" title="{f["van"]}–{f["tot"]} · {esc(f["titel"])}">{esc(f["titel"])}</a>'
    return f'<div class="track-label"><b>De organisatie</b><small><a href="{"../"*depth}organisatie.html">de bestuurlijke lijn →</a></small></div><div class="fasen">{cells}</div>'

def org_chart(key, titel, kleur_l, kleur_d, unit='× 1.000 euro'):
    rows = organisatie['financien']['reeks']
    vals = [r[key] for r in rows]
    lo, hi = min(0, min(vals)), max(vals)
    W, H, PAD_L, PAD_B, PAD_T = 960, 260, 46, 34, 16
    n = len(rows); bw = (W - PAD_L - 8) / n
    def y(v):
        return PAD_T + (H - PAD_T - PAD_B) * (1 - (v - lo) / (hi - lo))
    y0 = y(0)
    bars = ''
    peak = vals.index(max(vals)); last = n - 1
    for i, r in enumerate(rows):
        v = r[key]
        x = PAD_L + i * bw
        top, hgt = (y(v), y0 - y(v)) if v >= 0 else (y0, y(v) - y0)
        hgt = max(hgt, 1)
        tip = f'{r["p"]}: {v:,.0f} euro'.replace(',', '.') + (f' — {r["note"]}' if r['note'] else '')
        bars += f'<rect class="dbar" x="{x+1:.1f}" y="{top:.1f}" width="{bw-2:.1f}" height="{hgt:.1f}" rx="2"><title>{esc(tip)}</title></rect>'
        if i in (peak, last, 0):
            lab_y = top - 5 if v >= 0 else top + hgt + 12
            bars += f'<text class="dlab" x="{x+bw/2:.1f}" y="{lab_y:.1f}" text-anchor="middle">{round(v/1000)}</text>'
    ticks = ''
    for i, r in enumerate(rows):
        if i % 4 == 0 or i == n - 1:
            ticks += f'<text class="dtick" x="{PAD_L+i*bw+bw/2:.1f}" y="{H-8}" text-anchor="middle">{esc(r["p"][:4])}</text>'
    gl = ''
    step = 100000 if hi > 300000 else 50000
    v = step
    while v <= hi:
        gl += f'<line class="dgrid" x1="{PAD_L}" x2="{W-8}" y1="{y(v):.1f}" y2="{y(v):.1f}"/><text class="dtick" x="{PAD_L-6}" y="{y(v)+3:.1f}" text-anchor="end">{v//1000}</text>'
        v += step
    zero = f'<line class="dzero" x1="{PAD_L}" x2="{W-8}" y1="{y0:.1f}" y2="{y0:.1f}"/>'
    tbl = '<details class="dtable"><summary>Cijfers als tabel</summary><div style="overflow-x:auto"><table><tr><th>Boekjaar</th><th>Omzet</th><th>Resultaat</th><th>Eigen vermogen</th><th>Gebeurtenis</th></tr>' + ''.join(
        f'<tr><td>{esc(r["p"])}</td><td>{r["omzet"]:,}</td><td>{r["resultaat"]:,}</td><td>{r["vermogen"]:,}</td><td>{esc(r["note"])}</td></tr>'.replace(',', '.') for r in rows) + '</table></div></details>'
    return f'''<figure class="dfig" style="--dl:{kleur_l};--dd:{kleur_d}">
<figcaption><b>{esc(titel)}</b> <span class="mono">{esc(unit)}</span></figcaption>
<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(titel)} per boekjaar, 1999 tot 2025">{gl}{zero}{bars}{ticks}</svg>
{tbl if key == 'omzet' else ''}</figure>'''

def organisatie_page():
    fasen_html = ''
    for f in organisatie['fasen']:
        fasen_html += f'<section class="orgfase" id="{f["id"]}"><h2><span class="mono">{f["van"]}–{f["tot"]}</span> {esc(f["titel"])}</h2><p>{esc(f["tekst"])}</p></section>'
    def dl(items, k1, k2):
        return '<dl class="orgdl">' + ''.join(f'<dt>{esc(i[k1])}</dt><dd>{esc(i[k2])}</dd>' for i in items) + '</dl>'
    body = f'''<section><div class="wrap">
<div class="sec-head"><h2>De organisatie</h2><span class="mono">1999–2026 · zeven fasen</span></div>
<p class="lede">{esc(organisatie['intro'])}</p>
<div class="tl"><div class="tl-inner" style="--ny:{NY}"><div></div><div class="tl-years">{''.join(f'<span>{y}</span>' for y in range(Y0, Y1+1))}</div>{fasenband(0, link=True)}</div></div>
{fasen_html}
<div class="orggrid">
<div><h2>Besturing</h2>{dl(organisatie['besturing'], 'periode', 'vorm')}</div>
<div><h2>Huisvesting</h2>{dl(organisatie['huisvesting'], 'periode', 'plek')}</div>
</div>
<h2>Geld</h2>
<p class="lede">{esc(organisatie['financien']['toelichting'])}</p>
{org_chart('omzet', 'Omzet, fondsen en subsidies', '#B8803C', '#C08438')}
{org_chart('vermogen', 'Eigen vermogen', '#1F6F9B', '#3F9BD8')}
<h2>Bronnen</h2><ul class="docs">{''.join(f'<li>{esc(b)}</li>' for b in organisatie['bronnen'])}</ul>
</div></section>'''
    return page('De organisatie', body, desc='De bestuurlijke lijn van Stichting Formaat: rechtsvorm, besturing, huisvesting en financiën, 1999-2026.')

def facts_html(fm):
    cs = fm.get('cijfers') or []
    if not cs:
        return ''
    return '<div class="facts">' + ''.join(f'<div class="fact"><b>{esc(str(c.get("waarde","")))}</b><span>{esc(str(c.get("label","")))}</span></div>' for c in cs) + '</div>'

def media_html(gid):
    out = ''
    yt = media_by_group['youtube'].get(gid, [])
    if yt:
        out += '<h2>Video</h2><div class="videos">' + ''.join(
            f'<figure><div class="yt"><iframe loading="lazy" src="https://www.youtube-nocookie.com/embed/{v["id"]}" title="{esc(v["titel"])}" allowfullscreen></iframe></div><figcaption>{esc(v["titel"])} · {esc(v["duur"])}</figcaption></figure>' for v in yt) + '</div>'
    fs = [f for f in media_by_group['fotoseries'].get(gid, []) if f.get('gekozen')]
    if fs:
        out += '<h2>Beeld</h2><div class="gallery">' + ''.join(
            f'<figure><img loading="lazy" src="../beeld/{esc(img["bestand"])}" alt="{esc(img.get("alt",""))}"><figcaption>{esc(img.get("bijschrift",""))}{(" · foto: "+esc(img["fotograaf"])) if img.get("fotograaf") else ""}</figcaption></figure>'
            for f in fs for img in f['gekozen']) + '</div>'
    pubs = [p for p in media_by_group['publicaties'].get(gid, []) if p.get('openbaar')]
    if pubs:
        out += '<h2>Documenten</h2><ul class="docs">' + ''.join(f'<li><a href="{esc(p.get("url",""))}">{esc(p["titel"])}</a> <span class="mono">{esc(str(p.get("jaar","")))} · {esc(p.get("soort",""))}</span></li>' for p in pubs) + '</ul>'
    pers = media_by_group['pers'].get(gid, [])
    if pers:
        out += '<h2>In de pers</h2><ul class="pers">' + ''.join(f'<li><span class="mono">{esc(str(p.get("datum","")))}</span> {esc(p.get("medium",""))} — {esc(p.get("kop",""))}</li>' for p in sorted(pers, key=lambda p: str(p.get("datum","")))) + '</ul>'
    return out

def items_html(gid):
    its = sorted(items_by_group.get(gid, []), key=lambda p: (p['jaar_start'], p['seizoen'], p['naam']))
    if not its:
        return ''
    rows = ''
    for p in its:
        st = '' if p['status'] == 'uitgevoerd' else f' <em class="status">({esc(p["status"])})</em>'
        rows += f'<li id="{esc(p["id"])}"><span class="mono">{esc(p["seizoen"])}</span> <b>{esc(p["naam"])}</b>{st}<br><span class="small">{esc(p["beschrijving"])}</span></li>'
    return f'<h2>Activiteiten per seizoen</h2><ol class="items">{rows}</ol>'

def kaart_page(gid):
    k = kaarten[gid]; fm = k['fm']; g = G[gid]; s = S[g['spoor']]
    body_html = markdown.markdown(k['body'], extensions=['tables'])
    meta = ''
    for lab, key in [('Plaatsen', 'plaatsen'), ('Partners', 'partners'), ('Thema', 'thema')]:
        v = fm.get(key)
        if v:
            meta += f'<dt>{lab}</dt><dd>{esc(", ".join(map(str, v)))}</dd>'
    concept = '<span class="mono proto">concept · nog te controleren</span>' if fm.get('status') == 'concept' else ''
    ars = fm.get('arsenaal')
    ars_html = ''
    if ars:
        ars_html = f'<a class="ars-blok" href="{esc(ars.get("url", ARSENAAL))}"><span class="mono">→ Arsenaal van de joker</span><span class="ars-tekst">{esc(ars.get("tekst", ""))}</span></a>'
    body = f'''<article class="kaart" style="--c:{s['kleur']}">
<div class="wrap">
<div class="kaart-head">
  <div class="mono"><a href="../index.html#{s['id']}">{esc(s['naam'])}</a> · {esc(str(fm.get('periode', f"{g['van']}–{g['tot']}")))}</div>
  <h1>{esc(fm.get('titel', g['naam']))}</h1>
  <p class="sub">{esc(fm.get('ondertitel', ''))}</p>
  {concept}
</div>
<div class="kaart-grid">
<div class="kaart-body">{facts_html(fm)}{ars_html}{body_html}{media_html(gid)}{items_html(gid)}</div>
<aside class="kaart-side"><dl>{meta}</dl>
<p class="small">Deze kaart hoort bij het spoor <b>{esc(s['naam'])}</b>. Het <a href="{ARSENAAL}">Arsenaal van de joker</a> beschrijft de oefeningen en houdingen achter dit werk.</p>
</dl></aside>
</div></div></article>'''
    return page(fm.get('titel', g['naam']), body, depth=1, desc=fm.get('ondertitel', ''))

def index_page():
    n_items = len(projecten); n_groups = len(groepen); n_cards = len(kaarten)
    cards = ''
    for r in route[:3]:
        g = G[r['groep']]; s = S[g['spoor']]
        cards += f'<a class="mini" style="--c:{s["kleur"]}" href="kaarten/{g["id"]}.html"><span class="mono">{esc(s["naam"])}</span><b>{esc(r["titel"])}</b><em>{esc(r["vraag"])}</em></a>'
    body = f'''<section class="hero"><div class="wrap">
<span class="mono proto">{esc(site['status_banner'])}</span>
<h1>Formaat<br><span>1999–2025</span></h1>
<p class="lede">{esc(site['intro'])}</p>
<div class="hero-meta mono">{n_items} activiteiten · {n_groups} projectlijnen · {n_cards} kaarten · zusterproject van het <a href="{ARSENAAL}">Arsenaal van de joker</a></div>
</div></section>
<section><div class="wrap">
<div class="sec-head"><h2>Zes sporen, 26 jaar</h2><span class="mono">klik op een balk</span></div>
{tijdlijn(0)}
</div></section>
<section><div class="wrap">
<div class="sec-head"><h2>Maak kennis met het werk van Formaat</h2><a class="mono" href="route.html">hele route →</a></div>
<div class="minis">{cards}</div>
</div></section>'''
    return page('Tijdlijn', body)

def route_page():
    halts = ''
    for r in route:
        g = G[r['groep']]; s = S[g['spoor']]
        link = f'kaarten/{g["id"]}.html' if g['id'] in kaarten else f'alles.html#{g["id"]}'
        halts += f'<li style="--c:{s["kleur"]}"><a href="{link}"><span class="mono">halte {r["halte"]} · {esc(s["naam"])}</span><b>{esc(r["titel"])}</b><em>{esc(r["vraag"])}</em></a><a class="ars" href="{esc(r["arsenaal"])}">→ Arsenaal</a></li>'
    body = f'''<section><div class="wrap">
<div class="sec-head"><h2>Maak kennis met het werk van Formaat</h2><span class="mono">{len(route)} haltes</span></div>
<p class="lede">{esc(site['route_intro'])}</p>
<ol class="route">{halts}</ol>
</div></section>'''
    return page("Maak kennis met het werk van Formaat", body)

def thema_page():
    by = defaultdict(list)
    for g in groepen:
        for t in g.get('thema') or []:
            by[t].append(g)
    secs = ''
    for t in sorted(by):
        gs = sorted(by[t], key=lambda g: g['van'])
        secs += f'<h2 id="{esc(t)}">{esc(t.capitalize())}</h2><ul class="glist">' + ''.join(
            f'<li style="--c:{S[g["spoor"]]["kleur"]}"><a href="{"kaarten/"+g["id"]+".html" if g["id"] in kaarten else "alles.html#"+g["id"]}">{esc(g["naam"])}</a> <span class="mono">{g["van"]}–{g["tot"]}</span></li>' for g in gs) + '</ul>'
    body = f'<section><div class="wrap"><div class="sec-head"><h2>Thema\'s</h2><span class="mono">{len(by)} ingangen</span></div>{secs}</div></section>'
    return page("Thema's", body)

def alles_page():
    secs = ''
    for s in sporen:
        gs = sorted([g for g in groepen if g['spoor'] == s['id']], key=lambda g: g['van'])
        secs += f'<h2 id="{s["id"]}" style="--c:{s["kleur"]}">{esc(s["naam"])}</h2>'
        for g in gs:
            its = sorted(items_by_group.get(g['id'], []), key=lambda p: (p['jaar_start'], p['naam']))
            link = f' · <a href="kaarten/{g["id"]}.html">kaart</a>' if g['id'] in kaarten else ''
            secs += f'<details id="{g["id"]}"><summary><b>{esc(g["naam"])}</b> <span class="mono">{g["van"]}–{g["tot"]} · {len(its)}</span>{link}</summary><ol class="items">' + ''.join(
                f'<li id="{esc(p["id"])}"><span class="mono">{esc(p["seizoen"])}</span> <b>{esc(p["naam"])}</b>{"" if p["status"]=="uitgevoerd" else " <em class=status>("+esc(p["status"])+")</em>"}<br><span class="small">{esc(p["beschrijving"])}</span></li>' for p in its) + '</ol></details>'
    body = f'<section><div class="wrap"><div class="sec-head"><h2>Alle activiteiten</h2><span class="mono">{len(projecten)} items · {len(groepen)} lijnen</span></div><p class="lede">De volledige inventaris, per spoor en projectlijn. Ook wat gepland was en niet doorging staat erbij, met vermelding.</p>{secs}</div></section>'
    return page('Alle activiteiten', body)

def bronnen_page():
    pubs = sorted(media['publicaties'], key=lambda p: (str(p.get('soort','')), str(p.get('jaar',''))))
    by = defaultdict(list)
    for p in pubs:
        by[p.get('soort','overig')].append(p)
    def pub_li(p):
        t = esc(p['titel'])
        if p.get('openbaar') and p.get('url'):
            t = '<a href="%s">%s</a>' % (esc(p['url']), t)
        aut = (' · ' + esc(p['auteurs'])) if p.get('auteurs') else ''
        note = '' if p.get('openbaar') else ' <em class="small">(in archief, niet online)</em>'
        return '<li>%s <span class="mono">%s</span>%s%s</li>' % (t, esc(str(p.get('jaar', ''))), aut, note)
    secs = ''
    for soort in sorted(by):
        secs += f'<h2>{esc(soort.capitalize())}</h2><ul class="docs">' + ''.join(pub_li(p) for p in by[soort]) + '</ul>'
    yt = ''.join(f'<li><a href="https://www.youtube.com/watch?v={v["id"]}">{esc(v["titel"])}</a> <span class="mono">{esc(v["duur"])}</span></li>' for v in sorted(media['youtube'], key=lambda v: v['jaar_ca']))
    body = f'<section><div class="wrap"><div class="sec-head"><h2>Bronnen</h2><span class="mono">{len(pubs)} publicaties · {len(media["youtube"])} video\'s</span></div><p class="lede">{esc(site["bronnen_intro"])}</p><h2>Video (YouTube-kanaal Formaat231)</h2><ul class="docs">{yt}</ul>{secs}</div></section>'
    return page('Bronnen', body)

def over_page():
    body = f'<section><div class="wrap"><div class="sec-head"><h2>Over dit archief</h2></div><div class="prose">{markdown.markdown(open(D("data/over.md"), encoding="utf-8").read())}</div></div></section>'
    return page('Over', body)

def main():
    os.makedirs(os.path.join(OUT, 'kaarten'), exist_ok=True)
    os.makedirs(os.path.join(OUT, 'beeld'), exist_ok=True)
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(index_page())
    open(os.path.join(OUT, 'route.html'), 'w', encoding='utf-8').write(route_page())
    open(os.path.join(OUT, 'thema.html'), 'w', encoding='utf-8').write(thema_page())
    open(os.path.join(OUT, 'alles.html'), 'w', encoding='utf-8').write(alles_page())
    open(os.path.join(OUT, 'bronnen.html'), 'w', encoding='utf-8').write(bronnen_page())
    open(os.path.join(OUT, 'over.html'), 'w', encoding='utf-8').write(over_page())
    open(os.path.join(OUT, 'organisatie.html'), 'w', encoding='utf-8').write(organisatie_page())
    for gid in kaarten:
        if gid not in G:
            print('LET OP: kaart zonder projectgroep:', gid); continue
        open(os.path.join(OUT, 'kaarten', gid + '.html'), 'w', encoding='utf-8').write(kaart_page(gid))
    open(os.path.join(OUT, '.nojekyll'), 'w').close()
    print(f'gebouwd: {len(kaarten)} kaarten, {len(groepen)} lijnen, {len(projecten)} items → docs/')

if __name__ == '__main__':
    main()
