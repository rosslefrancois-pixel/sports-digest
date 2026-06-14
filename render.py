"""
render.py — turns a digest data dict into the final standalone HTML page.
Pure/offline: no network. Both generate.py (daily) and the initial seed use this,
so the design only ever lives in ONE place.
"""

# ---- crest marks (custom, color-matched — NOT official logos) ----
def _cup(sz):
    return (f'<svg viewBox="0 0 24 24" width="{sz}" height="{sz}" fill="none" '
            'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
            'stroke-linejoin="round"><path d="M7 4h10M8 4v3a4 4 0 0 0 8 0V4M12 11v4'
            'M8.5 19l.7-4h5.6l.7 4z"/></svg>')

def _octagon(sz):
    return (f'<svg viewBox="0 0 24 24" width="{sz}" height="{sz}" fill="none" '
            'stroke="currentColor" stroke-width="1.9" stroke-linejoin="round">'
            '<path d="M8 3.5h8L20.5 8v8L16 20.5H8L3.5 16V8z"/></svg>')

# inner content for each known crest key
def _crest_inner(key, sz):
    if key in ("nhl", "cup"):
        return _cup(sz)
    if key in ("ufc", "octagon"):
        return _octagon(sz)
    return {"bruins": "B", "pats": "NE", "patriots": "NE",
            "osu": "OSU"}.get(key, key[:3].upper())

def _color_class(key):
    return {"nhl": "c-nhl", "cup": "c-nhl", "bruins": "c-bruins",
            "pats": "c-pats", "patriots": "c-pats", "osu": "c-osu",
            "ufc": "c-ufc", "octagon": "c-ufc"}.get(key, "c-nhl")

def _section_crest(key):
    return f'<span class="crest sm {_color_class(key)}">{_crest_inner(key, 15)}</span>'

def _hero_mark(key):
    return f'<div class="tn-mark {_color_class(key)}">{_crest_inner(key, 18)}</div>'

def _esc_attr(s):  # minimal — for href/text we trust our own generator
    return (s or "").replace('"', "&quot;")

# ---- builders ----
def _hero(h):
    if not h or not h.get("rows"):
        return ""
    rows = ""
    for r in h["rows"]:
        rows += (
            '\n    <div class="tonight-row">'
            f'\n      {_hero_mark(r.get("crest","nhl"))}'
            '\n      <div class="tn-body">'
            f'\n        <div class="tn-title">{r.get("title","")}</div>'
            f'\n        <div class="tn-meta">{r.get("meta","")}</div>'
            '\n      </div>'
            f'\n      <div class="tn-time">{r.get("time","")}</div>'
            '\n    </div>'
        )
    return (
        '\n  <section class="hero reveal">'
        '\n    <div class="hero-head"><span class="eyebrow">'
        f'{h.get("title","Tonight")}</span></div>'
        f'\n    <div class="hero-sub">{h.get("sub","")}</div>'
        f'{rows}'
        '\n  </section>\n'
    )

def _board(rows):
    if not rows:
        return ""
    out = '\n    <div class="board">'
    for r in rows:
        main = r.get("main", "")
        if r.get("mono"):
            main = f'<span class="score">{main}</span>'
        if r.get("soft"):
            main += f' <span class="soft">· {r["soft"]}</span>'
        out += (
            '\n      <div class="board-row">'
            f'\n        <span class="board-label">{r.get("label","")}</span>'
            f'\n        <span class="board-main">{main}</span>'
            f'\n        <span class="board-tag">{r.get("tag","")}</span>'
            '\n      </div>'
        )
    out += '\n    </div>'
    return out

def _links(links):
    if not links:
        return ""
    out = '\n    <div class="links">'
    for l in links:
        out += (
            f'\n      <a class="lnk" href="{_esc_attr(l.get("url","#"))}" '
            'target="_blank" rel="noopener">'
            f'\n        <span class="tx">{l.get("text","")}'
            f'<span class="src">{l.get("src","")}</span></span>'
            '<span class="chev">&rsaquo;</span>'
            '\n      </a>'
        )
    out += '\n    </div>'
    return out

def _notes(notes):
    if not notes:
        return ""
    out = '\n    <div class="notes">'
    for n in notes:
        out += f'\n      <div class="note">{n}</div>'
    out += '\n    </div>'
    return out

def _bouts(bouts):
    if not bouts:
        return ""
    out = '\n    <div class="bouts">'
    for b in bouts:
        cls = "bout title" if b.get("title") else "bout"
        out += (
            f'\n      <div class="{cls}"><span class="vs">{b.get("vs","")}</span>'
            f'<span class="wc">{b.get("wc","")}</span></div>'
        )
    out += '\n    </div>'
    return out

def _pill(p):
    if not p:
        return ""
    cls = "pill"
    if p.get("live"):
        cls = "pill live"
    elif p.get("accent"):
        cls = "pill accent"
    return f'<span class="{cls}">{p.get("text","")}</span>'

def _section(s):
    key = s.get("key", "nhl")
    return (
        f'\n  <section class="card t-{key} reveal">'
        '\n    <div class="sec-head">'
        f'\n      <div class="sec-name">{_section_crest(s.get("crest", key))}'
        f'<span class="nm">{s.get("name","")}</span></div>'
        f'\n      {_pill(s.get("pill"))}'
        '\n    </div>'
        f'\n    <div class="ctx">{s.get("ctx","")}</div>'
        f'{_board(s.get("board"))}'
        f'{_bouts(s.get("bouts"))}'
        f'{_links(s.get("links"))}'
        f'{_notes(s.get("notes"))}'
        '\n  </section>\n'
    )

def render(data):
    hero = _hero(data.get("hero"))
    sections = "".join(_section(s) for s in data.get("sections", []))
    html = _TEMPLATE
    html = html.replace("%%DATE_LABEL%%", data.get("date_label", ""))
    html = html.replace("%%HERO%%", hero)
    html = html.replace("%%SECTIONS%%", sections)
    html = html.replace("%%SOURCES%%", data.get("sources", ""))
    html = html.replace("%%STAMP%%", data.get("updated_label", ""))
    return html

# ---- the page shell (design lives here, once) ----
_TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#0B0E13">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/icon-192.png">
<title>Daily Sports Digest</title>
<style>
  :root{
    --bg:#0B0E13; --bg-2:#0E121A; --surface:#151A22; --surface-2:#1B212B;
    --border:#252C38; --ink:#EAEEF5; --ink-dim:#9AA4B4; --ink-faint:#69727F;
    --ice:#8FC0E6; --bruins:#FFB81C; --pats:#E0394E; --pats-navy:#0A2342;
    --osu:#E23636; --ufc:#FF3B3B; --live:#36D399;
    --mono:"Roboto Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
    --sans:"Roboto","Google Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  html{ -webkit-text-size-adjust:100%; }
  body{
    font-family:var(--sans);
    background:radial-gradient(120% 80% at 50% -10%, #131A26 0%, rgba(19,26,38,0) 55%), var(--bg);
    color:var(--ink); line-height:1.45; min-height:100vh;
    padding:0 0 calc(34px + env(safe-area-inset-bottom));
    -webkit-font-smoothing:antialiased;
  }
  .wrap{ max-width:540px; margin:0 auto; padding:0 14px; }
  header.mast{ position:sticky; top:0; z-index:20;
    background:linear-gradient(180deg, rgba(11,14,19,0.96) 0%, rgba(11,14,19,0.82) 70%, rgba(11,14,19,0) 100%);
    backdrop-filter:blur(8px); -webkit-backdrop-filter:blur(8px);
    padding:calc(14px + env(safe-area-inset-top)) 0 14px; }
  .mast-row{ display:flex; align-items:baseline; justify-content:space-between; gap:10px; }
  .mast-title{ font-size:13px; font-weight:800; letter-spacing:.22em; text-transform:uppercase;
    color:var(--ink); display:flex; align-items:center; gap:9px; }
  .mast-title .dot{ width:8px; height:8px; border-radius:50%; background:var(--live);
    box-shadow:0 0 0 4px rgba(54,211,153,.16); }
  .mast-date{ font-family:var(--mono); font-size:11.5px; letter-spacing:.04em; color:var(--ink-dim); white-space:nowrap; }
  .mast-rule{ height:1px; margin-top:12px;
    background:linear-gradient(90deg, var(--ice), rgba(143,192,230,0) 60%); opacity:.6; }
  .hero{ margin-top:16px; border:1px solid var(--border); border-radius:18px;
    background:radial-gradient(140% 120% at 85% 0%, rgba(143,192,230,.10), rgba(143,192,230,0) 50%),
      linear-gradient(180deg, var(--surface-2), var(--surface)); overflow:hidden; }
  .hero-head{ display:flex; align-items:center; gap:10px; padding:15px 16px 4px; }
  .eyebrow{ font-size:11px; font-weight:800; letter-spacing:.26em; text-transform:uppercase; color:var(--ice); }
  .hero-sub{ font-size:12px; color:var(--ink-dim); padding:0 16px 12px; }
  .tonight-row{ display:flex; align-items:center; gap:13px; padding:13px 16px; border-top:1px solid var(--border); }
  .tn-mark{ width:34px; height:34px; border-radius:9px; flex:none; display:grid; place-items:center;
    font-size:15px; font-weight:800; background:rgba(255,255,255,.04); border:1px solid var(--border); }
  .tn-body{ flex:1; min-width:0; }
  .tn-title{ font-size:14.5px; font-weight:700; color:var(--ink); }
  .tn-meta{ font-size:11.5px; color:var(--ink-dim); margin-top:1px; }
  .tn-time{ font-family:var(--mono); font-size:12px; font-weight:600;
    background:rgba(54,211,153,.12); border:1px solid rgba(54,211,153,.35); color:var(--live);
    padding:5px 9px; border-radius:999px; white-space:nowrap; letter-spacing:.02em; }
  .card{ position:relative; margin-top:14px; border:1px solid var(--border); border-radius:16px;
    background:linear-gradient(180deg, var(--surface), var(--bg-2)); overflow:hidden; }
  .card::before{ content:""; position:absolute; left:0; top:0; bottom:0; width:4px; background:var(--accent,#888); }
  .card.t-nhl{ --accent:var(--ice); } .card.t-bruins{ --accent:var(--bruins); }
  .card.t-pats{ --accent:var(--pats); } .card.t-osu{ --accent:var(--osu); } .card.t-ufc{ --accent:var(--ufc); }
  .sec-head{ display:flex; align-items:center; justify-content:space-between; gap:10px; padding:14px 15px 10px 18px; }
  .sec-name{ display:flex; align-items:center; gap:9px; font-size:15px; font-weight:800; letter-spacing:.02em; }
  .sec-name .nm{ text-transform:uppercase; letter-spacing:.08em; font-size:13px; color:var(--accent); }
  .pill{ font-family:var(--mono); font-size:10.5px; font-weight:600; letter-spacing:.06em; text-transform:uppercase;
    padding:4px 9px; border-radius:999px; white-space:nowrap;
    color:var(--ink-dim); background:rgba(255,255,255,.04); border:1px solid var(--border); }
  .pill.live{ color:var(--live); background:rgba(54,211,153,.12); border-color:rgba(54,211,153,.32); }
  .pill.accent{ color:var(--accent); background:color-mix(in srgb, var(--accent) 14%, transparent);
    border-color:color-mix(in srgb, var(--accent) 38%, transparent); }
  .ctx{ font-size:12.5px; font-style:italic; color:var(--ink-dim); padding:0 18px 12px; }
  .board{ margin:0 14px 12px; border:1px solid var(--border); border-radius:12px; background:rgba(0,0,0,.28); overflow:hidden; }
  .board-row{ display:flex; align-items:center; justify-content:space-between; gap:12px; padding:10px 13px; }
  .board-row + .board-row{ border-top:1px solid var(--border); }
  .board-label{ font-size:10.5px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--ink-faint); }
  .board-main{ font-size:13.5px; color:var(--ink); font-weight:600; }
  .board-main .score{ font-family:var(--mono); letter-spacing:.04em; }
  .board-main .soft{ color:var(--ink-dim); font-weight:500; }
  .board-tag{ font-family:var(--mono); font-size:11px; color:var(--ink-dim); white-space:nowrap; }
  .links{ padding:2px 8px 6px; }
  .lnk{ display:flex; align-items:center; gap:11px; padding:11px 10px; border-radius:10px;
    color:var(--ink); text-decoration:none; -webkit-tap-highlight-color:transparent; }
  .lnk + .lnk{ border-top:1px solid rgba(255,255,255,.05); }
  .lnk:active{ background:rgba(255,255,255,.05); }
  .lnk .tx{ flex:1; font-size:13.5px; line-height:1.35; }
  .lnk .src{ display:block; font-size:11px; color:var(--ink-faint); margin-top:2px; }
  .lnk .chev{ flex:none; color:var(--accent); font-size:15px; opacity:.85; }
  .notes{ padding:6px 18px 16px; }
  .note{ position:relative; padding:7px 0 7px 16px; font-size:13px; color:#D4DAE3; line-height:1.5; }
  .note + .note{ border-top:1px solid rgba(255,255,255,.045); }
  .note::before{ content:""; position:absolute; left:0; top:14px; width:6px; height:6px; border-radius:50%;
    background:var(--accent); opacity:.85; }
  .note b{ color:var(--ink); font-weight:700; }
  .bouts{ padding:2px 14px 14px; }
  .bout{ display:flex; align-items:center; gap:10px; padding:9px 4px; font-size:13px; }
  .bout + .bout{ border-top:1px solid rgba(255,255,255,.05); }
  .bout .vs{ flex:1; color:var(--ink); } .bout .vs b{ font-weight:700; }
  .bout .wc{ font-family:var(--mono); font-size:10px; letter-spacing:.04em; color:var(--ink-faint);
    text-transform:uppercase; white-space:nowrap; }
  .bout.title .wc{ color:var(--ufc); }
  .crest{ display:grid; place-items:center; flex:none; border:1px solid transparent; border-radius:8px;
    font-family:var(--sans); font-weight:800; }
  .crest.sm{ width:26px; height:26px; border-radius:7px; font-size:11px; letter-spacing:.02em; }
  .crest svg{ display:block; }
  .c-nhl{ background:linear-gradient(180deg,#1b2836,#101824); border-color:rgba(143,192,230,.45); color:var(--ice); }
  .c-bruins{ background:#000; border-color:rgba(255,184,28,.55); color:var(--bruins); }
  .c-pats{ background:var(--pats-navy); border-color:rgba(224,57,78,.55); color:var(--pats); }
  .c-osu{ background:#A50F0F; border-color:rgba(255,255,255,.18); color:#fff; }
  .crest.sm.c-osu{ font-size:9px; }
  .c-ufc{ background:#000; border-color:rgba(255,59,59,.5); color:var(--ufc); }
  footer{ margin-top:20px; padding:0 6px; }
  .src-line{ font-size:10.5px; color:var(--ink-faint); line-height:1.7; }
  .stamp{ font-family:var(--mono); font-size:10.5px; color:var(--ink-faint); margin-top:10px;
    display:flex; gap:6px; align-items:center; }
  .stamp .dot{ width:5px; height:5px; border-radius:50%; background:var(--ink-faint); }
  @media (prefers-reduced-motion:no-preference){
    .reveal{ opacity:0; transform:translateY(10px); animation:rise .5s cubic-bezier(.2,.7,.2,1) forwards; }
    .reveal:nth-child(1){animation-delay:.02s} .reveal:nth-child(2){animation-delay:.08s}
    .reveal:nth-child(3){animation-delay:.14s} .reveal:nth-child(4){animation-delay:.20s}
    .reveal:nth-child(5){animation-delay:.26s} .reveal:nth-child(6){animation-delay:.32s}
    @keyframes rise{ to{ opacity:1; transform:none; } }
    .pill.live{ animation:glow 2.4s ease-in-out infinite; }
    @keyframes glow{ 0%,100%{ box-shadow:0 0 0 0 rgba(54,211,153,0);} 50%{ box-shadow:0 0 0 4px rgba(54,211,153,.10);} }
  }
  a:focus-visible,.lnk:focus-visible{ outline:2px solid var(--ice); outline-offset:2px; border-radius:8px; }
</style>
</head>
<body>
<div class="wrap">
  <header class="mast">
    <div class="mast-row">
      <div class="mast-title"><span class="dot"></span>Sports Digest</div>
      <div class="mast-date">%%DATE_LABEL%%</div>
    </div>
    <div class="mast-rule"></div>
  </header>
%%HERO%%%%SECTIONS%%
  <footer>
    <div class="src-line">Sources — %%SOURCES%%</div>
    <div class="stamp"><span class="dot"></span>Updated %%STAMP%%</div>
  </footer>
</div>
<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('sw.js').catch(function(){});
    });
  }
</script>
</body>
</html>
'''
