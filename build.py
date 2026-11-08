#!/usr/bin/env python3
"""Convert the three Design artboards into a static, responsive site in ./site."""
import re, os, shutil, html, hashlib

SRC = {"Main": "index.html", "MEI": "mei/index.html", "Siemens": "siemens/index.html"}
COLORS = {"green": "#5B8130", "yellow": "#FFC000", "orange": "#FF9D4C"}
IMG = {
    "1bfb746e4ecd7b28120c0253edb2a6c0": ("kvp-logo-dum.png", "kvp-logo.png"),
    "725a18713a6b4b250b6785aaec01105b": ("znacka.png", "znacka-spolehlivosti.png"),
    "a0c0f8b6de60fee93a6894d63405ce51": ("hero.jpg", "zahradni-slavnost.jpg"),
    "f60e541a384efde4dac0498c4e7cd68f": ("jirka.jpg", "asistent-jirka.jpg"),
    "f8659ac51fa95aa5ea9b69cf63e51ced": ("jana.jpg", "klientka.jpg"),
    "c72ac2ec2416a7cfa3b0a92f8b6b516c": ("flag.jpg", "tym-vlajka.jpg"),
    "5271545ebb21913aac081bac3e896eae": ("corridor.jpg", "asistence-zvedak.jpg"),
    "6970534ab09aa490bc25560e8d3664f1": ("tym-chodba.jpg", "tym-chodba.jpg"),
    "41eabe9016be61cd1ca36540192b8213": ("drabek2.png", "tomas-drabek.png"),
}
META = {
    "Main": ("kvpslavi.cz – 35 let Klubu vozíčkářů Petýrkova",
             "Klub vozíčkářů Petýrkova slaví 35 let. Hledáme 10 firem, které s námi oslaví jubilejní rok a podpoří osobní asistenci v Praze 11."),
    "MEI": ("Pozvánka pro MEI Property Services – 35 let KVP",
            "Osobní pozvánka pro MEI Property Services: staňte se partnerem oslavy 35 let Klubu vozíčkářů Petýrkova."),
    "Siemens": ("Pozvánka pro Siemens – 35 let KVP",
                "Osobní pozvánka pro Siemens: staňte se partnerem oslavy 35 let Klubu vozíčkářů Petýrkova."),
}

OUT = "site"
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(f"{OUT}/img", exist_ok=True)
for blob, (src, dst) in IMG.items():
    shutil.copy(f"/mnt/user-data/outputs/img/{src}", f"{OUT}/img/{dst}")

# ---------- static expansion of the template loops ----------
def slots_main(joined=3, negotiating=1):
    out = []
    for i in range(10):
        filled = i < joined
        pending = (not filled) and i < joined + negotiating
        fill = COLORS["yellow"] if filled else (COLORS["orange"] if pending else "#7FA353")
        out.append(f'<div class="bar-seg" style="background: {fill}"></div>')
    return "\n".join(out)

def slots_sub(names, mei_label):
    out = []
    for i in range(10):
        filled = i < len(names)
        talking = i == len(names)
        mei = i == len(names) + 1
        if filled:
            fill, border, bs, lc, sc = "#FFFFFF", "#FFFFFF", "solid", "#141414", "#6B6B68"
            label, sub = names[i], "Partner oslavy"
        elif talking:
            fill, border, bs, lc, sc = COLORS["orange"], COLORS["orange"], "solid", "#141414", "#4A2A0A"
            label, sub = "Partner č. 4", "Jednáme o spolupráci"
        elif mei:
            fill, border, bs, lc, sc = COLORS["yellow"], COLORS["yellow"], "solid", "#141414", "#3B3200"
            label, sub = mei_label, "rezervováno pro vás"
        else:
            fill, border, bs, lc, sc = "transparent", "#8CAE63", "dashed", "#DCE8CC", "#B5C99A"
            label, sub = "Volné místo", f"#{i+1}"
        out.append(
            f'<div class="tile" style="border: 1px {bs} {border}; background: {fill}">'
            f'<div style="font-size: 13px; font-weight: 700; color: {lc}">{label}</div>'
            f'<div style="font-size: 12px; font-weight: 600; color: {sc}">{sub}</div></div>')
    return "\n".join(out)

# ---------- inline style -> class ----------
class Styler:
    def __init__(self):
        self.rules = {}  # css text -> class
    def cls(self, css):
        css = re.sub(r"\s+", " ", css.strip().rstrip(";")).strip()
        if css not in self.rules:
            self.rules[css] = f"s{len(self.rules)+1}"
        return self.rules[css]
    def sheet(self):
        return "\n".join(f".{c}{{{css}}}" for css, c in self.rules.items())

def convert(name, path):
    s = open(f"{name}.dc.html", encoding="utf-8").read()
    body = s[s.index("<x-dc>") + 6 : s.index("</x-dc>")]
    body = re.sub(r"<helmet>.*?</helmet>", "", body, flags=re.S)
    for k, v in COLORS.items():
        body = body.replace("{{" + k + "}}", v)
    for blob, (_, dst) in IMG.items():
        body = body.replace(f"/_blob/{blob}", f"/img/{dst}")
    # loops
    if name == "Main":
        body = body.replace("{{joined}}", "3")
        body = re.sub(r"<sc-for.*?</sc-for>", slots_main(), body, flags=re.S)
    else:
        mei_label = "MEI Property Services" if name == "MEI" else "Siemens"
        body = re.sub(r"<sc-for.*?</sc-for>",
                      slots_sub(["PRE", "Westfield Chodov", "Rozsviťme Česko"], mei_label), body, flags=re.S)
    assert "{{" not in body, re.findall(r"{{[^}]+}}", body)[:5]

    # root wrapper: make fluid
    body = re.sub(r'<div style="width: 1280px; height: \d+px; box-sizing: border-box; background: #FFFFFF; color: #141414; display: flex; flex-direction: column;( overflow: hidden;)? position: relative">',
                  '<div class="page">', body, count=1)
    assert 'class="page"' in body

    # semantic section classes from the HTML comments
    sec_map = [("HEADER", "sec-header"), ("HERO", "sec-hero"), ("BENTO", "sec-bento"), ("THE ASK", "sec-ask"),
               ("WHERE THE MONEY GOES", "sec-money"), ("WHAT PAST GIFTS DID", "sec-money"), ("THE OFFER", "sec-ask"),
               ("WHAT MEI GETS", "sec-benefits"), ("BENEFITS", "sec-benefits"), ("LETTER", "sec-letter"),
               ("PHOTO STRIP", "sec-photos"), ("STEPS", "sec-steps"), ("CONTACT", "sec-contact"), ("FOOTER", "sec-footer")]
    def tag_section(m):
        comment, tag = m.group(1), m.group(2)
        cls = next((c for k, c in sec_map if k in comment), "")
        return f"<!-- {comment} -->\n<{tag} class=\"{cls}\" "
    body = re.sub(r"<!-- ([^>]*?) -->\n<(section|header|footer) ", tag_section, body)

    st = Styler()
    def to_class(m):
        pre, css, post = m.group(1), m.group(2), m.group(3)
        existing = re.search(r'class="([^"]*)"', pre + post)
        c = st.cls(css)
        if existing:
            merged = (existing.group(1) + " " + c).strip()
            full = (pre + post).replace(existing.group(0), f'class="{merged}"', 1)
            return "<" + full.replace(">", ">", 1) if False else re.sub(r'class="([^"]*)"', f'class="{merged}"', pre + post, count=1)
        return f'{pre}class="{c}"{post}'
    # handle each opening tag with a style attribute
    def tag_sub(m):
        tag = m.group(0)
        sm = re.search(r'\sstyle="([^"]*)"', tag)
        if not sm: return tag
        c = st.cls(sm.group(1))
        tag = tag.replace(sm.group(0), "", 1)
        cm = re.search(r'\sclass="([^"]*)"', tag)
        if cm:
            tag = tag.replace(cm.group(0), f' class="{cm.group(1)} {c}"', 1)
        else:
            tag = re.sub(r"^<(\w+)", lambda mm: f"<{mm.group(1)} class=\"{c}\"", tag, count=1)
        return tag
    body = re.sub(r"<[a-zA-Z][^>]*>", tag_sub, body)

    # responsive overrides derived from the generated classes
    mob = []
    for css, c in st.rules.items():
        r = []
        if re.search(r"grid-template-columns: repeat\((\d+), minmax", css):
            n = int(re.search(r"repeat\((\d+)", css).group(1))
            if n == 12: r.append("grid-template-columns: 1fr")
            elif n >= 5: r.append("grid-template-columns: repeat(2, minmax(0, 1fr))")
            elif n in (3, 4): r.append("grid-template-columns: 1fr")
            elif n == 2: r.append("grid-template-columns: 1fr")
        if "grid-column: span" in css: r.append("grid-column: span 1")
        if "grid-row: span" in css: r.append("grid-row: span 1")
        if "grid-template-rows:" in css: r.append("grid-template-rows: auto")
        if "grid-template-columns: 72px 1fr" in css: r.append("grid-template-columns: 40px 1fr; gap: 12px")
        if re.search(r"padding: \d+px 64px", css) or re.search(r"padding: \d+px 64px \d+px 64px", css) or "padding: 0 64px" in css:
            css2 = re.sub(r"(\d+)px 64px(?: (\d+)px 64px)?", lambda m: f"{min(int(m.group(1)),56)}px 20px" + (f" {min(int(m.group(2)),56)}px 20px" if m.group(2) else ""), css)
            pad = re.search(r"padding: [^;]+", css2).group(0); r.append(pad)
        if "margin: 0 64px" in css: r.append("margin: 0 20px")
        if "padding: 72px" in css: r.append("padding: 32px 20px")
        if "padding: 64px" in css: r.append("padding: 32px 20px")
        fs = re.search(r"font-size: (\d+)px", css)
        if fs:
            v = int(fs.group(1))
            if v >= 80: r.append("font-size: 40px")
            elif v >= 56: r.append("font-size: 34px")
            elif v >= 44: r.append("font-size: 30px")
            elif v >= 36: r.append("font-size: 28px")
        if "min-height: 460px" in css or "min-height: 520px" in css: r.append("min-height: 260px")
        if re.search(r"height: (300|320|340|260|224|230|220)px", css) and "object-fit" in css: r.append("height: 220px")
        if re.search(r"^height: (300|320|260)px; overflow: hidden", css) or ("overflow: hidden; height: 300px" in css): r.append("height: 220px")
        if "width: 460px; height: 460px" in css: r.append("width: 100%; height: auto; aspect-ratio: 1 / 1")
        if "max-width: 1150px" in css or "max-width: 1140px" in css or "max-width: 1100px" in css: r.append("max-width: 100%")
        if "display: flex" in css and "justify-content: space-between" in css and "align-items: center" in css and "gap" in css and "padding: 20px" in css:
            r.append("flex-direction: column; align-items: flex-start; gap: 14px")
        if "display: flex" in css and "justify-content: space-between" in css and "align-items: flex-end" in css:
            r.append("flex-direction: column; align-items: flex-start")
        if "display: flex; gap: 12px; align-items: center" in css or "display: flex; gap: 16px; align-items: center" in css:
            r.append("flex-wrap: wrap")
        if "display: flex; align-items: flex-end; justify-content: space-between" in css:
            r.append("flex-direction: column; align-items: flex-start")
        if "text-align: right" in css: r.append("text-align: left")
        if "justify-content: space-between; align-items: baseline" in css: r.append("flex-wrap: wrap; gap: 8px")
        if r: mob.append(f".{c}{{{'; '.join(r)}}}")
    title, desc = META[name]
    css = f"""
*{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%}}
body{{margin:0;font-family:'Manrope',Helvetica,Arial,sans-serif;background:#FFFFFF;color:#141414}}
a{{color:#5B8130}}a:hover{{color:#3F5C20}}
img{{max-width:100%}}
.page{{width:100%;max-width:1280px;margin:0 auto;background:#FFFFFF;color:#141414;display:flex;flex-direction:column;position:relative}}
.bar-seg{{height:14px;border-radius:999px}}
.tile{{height:96px;border-radius:18px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;text-align:center;padding:8px}}
{st.sheet()}
@media (max-width: 900px){{
.sec-header{{flex-wrap:wrap;gap:12px}}
{chr(10).join(mob)}
.sec-footer{{flex-direction:column;align-items:flex-start;gap:12px}}
}}
@media (max-width: 480px){{
.tile{{height:84px}}
}}
"""
    doc = f"""<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="/img/zahradni-slavnost.jpg">
<link rel="icon" type="image/png" href="/img/kvp-logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Instrument+Serif:ital@0;1&display=swap">
<style>{css}</style>
</head>
<body>
{body.strip()}
</body>
</html>
"""
    out = f"{OUT}/{path}"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(doc)
    print(name, "->", out, len(doc), "bytes,", len(st.rules), "classes,", len(mob), "mobile rules")

for n, p in SRC.items():
    convert(n, p)
