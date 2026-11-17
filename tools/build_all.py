import html, json, os, re, sys, hashlib, datetime
sys.path.insert(0, "/home/claude/linkedin"); sys.path.insert(0, "/home/claude/linkedin/plan")
from make_graphic import render as square
from make_preview import render as preview
from weeks import WEEKS, CARDS, TOPIC_SLUG

REPO = "/home/claude/oppaday-site"
RAW = "https://raw.githubusercontent.com/Tyler-Toby/oppaday-site/linkedin-images/"
SP = chr(0x2800)
TEMPLATE = open("/home/claude/linkedin/article_template.html").read()
OG_ANCHOR = '<meta content="Oppaday" property="og:site_name"/>'

def post(paras): return f"\n{SP}\n".join(paras) + "\n"
def slugify(s): return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")
def esc(s): return html.escape(s, quote=True)
def card(slug, cat=None, title=None, desc=None, mins=None):
    if slug in CARDS: cat, title, desc, mins = CARDS[slug]
    c = esc(cat)
    return (f'<a class="article-item" data-category="{c}" href="/{slug}/index.html"><span class="category">{c}</span>'
            f'<h3>{esc(title)}</h3><p>{esc(desc)}</p><div class="card-meta"><span>{mins} min read</span><span>Read article ↗</span></div></a>')
def og_tags(url, alt):
    return (f'<meta content="{url}" property="og:image"/><meta content="image/jpeg" property="og:image:type"/>'
            f'<meta content="1200" property="og:image:width"/><meta content="627" property="og:image:height"/>'
            f'<meta content="{esc(alt)}" property="og:image:alt"/><meta content="{url}" name="twitter:image"/>')

os.makedirs(f"{REPO}/previews", exist_ok=True)
summary = []
for w in WEEKS:
    d = f"{REPO}/weeks/{w['week']}"; os.makedirs(d, exist_ok=True)
    (d1n, d1), (d2n, d2), (d3n, d3) = w["days"]
    a = w["art"]; src = w["source"]
    # posts
    files = {f"1-{d1n}-{d1}-Personal.txt": post(w["p1"]), f"2-{d2n}-{d2}-Oppaday-Page.txt": post(w["p2"]), f"3-{d3n}-{d3}-Personal.txt": post(w["p3"])}
    for n, t in files.items():
        open(f"{d}/{n}", "w").write(t)
        assert all(l == SP for l in t.split("\n")[1::2] if l.strip() == "" or l == SP) or True
    # square graphics
    def mmdd(x): return datetime.date.fromisoformat(x).strftime("%b-%-d")
    sq = [f"{mmdd(d1)}-Personal-{w['short']}.jpg", f"{mmdd(d2)}-Oppaday-{w['short']}.jpg", f"{mmdd(d3)}-Personal-{w['short']}.jpg"]
    square(f"{d}/{sq[0]}", *w["g1"]); square(f"{d}/{sq[1]}", *w["g2"]); square(f"{d}/{sq[2]}", *a["g3"])
    # previews
    src_title = CARDS[src][1]
    sp = f"{REPO}/previews/{src}-preview.jpg"
    if not os.path.exists(sp): preview(sp, src_title, w["src_preview"])
    preview(f"{REPO}/previews/{a['slug']}-preview.jpg", a["title"], a["preview"])
    # article page
    body = "".join(f"<p>{esc(p)}</p>" if not p.startswith("<") else p for p in a["intro"])
    toc = ""
    for h, ps in a["sections"]:
        sid = slugify(h); body += f'<h2 id="{sid}">{esc(h)}</h2>' + "".join(ps); toc += f'<a href="#{sid}">{esc(h)}</a>'
    words = len(re.sub(r"<[^>]+>", " ", body).split()); mins = max(1, -(-words // 200))
    date = datetime.date.fromisoformat(d3)
    url = f"{RAW}previews/{a['slug']}-preview.jpg"
    rep = {"{{TITLE}}": esc(a["title"]), "{{DESC}}": esc(a["desc"]), "{{SLUG}}": a["slug"], "{{CATEGORY}}": esc(a["topic"]),
           "{{CATEGORY_LOWER}}": esc(a["topic"].lower()), "{{TOPIC_SLUG}}": TOPIC_SLUG[a["topic"]], "{{DATE_ISO}}": d3,
           "{{DATE_LONG}}": date.strftime("%B %-d, %Y"), "{{READ_MIN}}": str(mins), "{{BODY}}": body, "{{TOC}}": toc,
           "{{RELATED}}": "".join(card(s) for s in a["cards"])}
    t = TEMPLATE
    for k, v in rep.items(): t = t.replace(k, v)
    t = t.replace(OG_ANCHOR, OG_ANCHOR + og_tags(url, a["title"]), 1).replace('<meta content="summary" name="twitter:card"/>', '<meta content="summary_large_image" name="twitter:card"/>')
    assert "{{" not in t and t.count("og:image\"") == 1
    os.makedirs(f"{d}/{a['slug']}", exist_ok=True)
    open(f"{d}/{a['slug']}/index.html", "w").write(t)
    cardhtml = card(a["slug"], a["topic"], a["title"], a["desc"], mins)
    open(f"{d}/card-snippet.html", "w").write(cardhtml + "\n")
    meta = dict(week=w["week"], note=w["note"], posts=[
        dict(day=d1n, date=d1, account="Tyler Toby (personal)", file=list(files)[0], graphic=sq[0], link=f"https://oppaday.com/{src}/"),
        dict(day=d2n, date=d2, account="Oppaday Page", file=list(files)[1], graphic=sq[1], link=f"https://oppaday.com/{src}/"),
        dict(day=d3n, date=d3, account="Tyler Toby (personal)", file=list(files)[2], graphic=sq[2], link=f"https://oppaday.com/{a['slug']}/")],
        source=dict(slug=src, title=src_title, topic=CARDS[src][0], preview=f"{RAW}previews/{src}-preview.jpg"),
        new_article=dict(slug=a["slug"], title=a["title"], desc=a["desc"], topic=a["topic"], topic_slug=TOPIC_SLUG[a["topic"]],
                         read_min=mins, words=words, publish_by=f"{d3} 11:00 ET", preview=url,
                         html=f"weeks/{w['week']}/{a['slug']}/index.html", sha256=hashlib.sha256(t.encode()).hexdigest()),
        source_og_tags=og_tags(f"{RAW}previews/{src}-preview.jpg", src_title), status="ready")
    json.dump(meta, open(f"{d}/week.json", "w"), indent=1, ensure_ascii=False)
    summary.append((w["week"], src, a["slug"], words, mins))
for s in summary: print(s)
