#!/usr/bin/env python3
"""
generate.py — researches the day's sports news via Claude + web search,
then renders index.html using render.py. Run by the daily GitHub Action.

Needs env var ANTHROPIC_API_KEY. On any failure it exits non-zero so the
Action fails loudly and the last good index.html stays committed.
"""
import os, sys, json, datetime, urllib.request, urllib.error
import render

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("DIGEST_MODEL", "claude-sonnet-4-6")
API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Eastern time label without external tz deps (EDT Mar-Nov, EST otherwise — close enough for a header stamp)
def eastern_now():
    utc = datetime.datetime.now(datetime.timezone.utc)
    edt = 3 <= utc.month <= 11
    return utc - datetime.timedelta(hours=4 if edt else 5), ("ET")

NOW_ET, TZ = eastern_now()
DATE_LABEL = NOW_ET.strftime("%a · %b %-d · %Y").upper()
DATE_LONG  = NOW_ET.strftime("%A, %B %-d, %Y")
UPDATED    = NOW_ET.strftime("%a, %b %-d, %Y · %-I:%M %p ") + TZ

SCHEMA = r'''
Return ONE JSON object, nothing else (no prose, no markdown fences). Schema:

{
  "date_label": "%s",
  "date_long":  "%s",
  "updated_label": "%s",
  "hero": {                      // OPTIONAL. Include ONLY if something relevant is on TODAY
    "title": "Tonight",          //   (an NHL game, a UFC event, or a Bruins/Patriots/Ohio State game).
    "sub": "one short line",     //   If nothing is on today, OMIT the whole "hero" key.
    "rows": [ {"crest":"nhl|ufc|bruins|pats|osu","title":"...","meta":"...","time":"8:00 ET"} ]
  },
  "sections": [                  // EXACTLY these five, in this order: nhl, bruins, pats, osu, ufc
    {
      "key": "nhl",              // one of: nhl, bruins, pats, osu, ufc
      "name": "NHL · Cup Final", // short header label
      "crest": "nhl",            // same key
      "pill": {"text":"Tonight · 8:00 ET","live":true},   // live:true for tonight; else {"text":"Offseason","accent":true}
      "ctx": "one italic context sentence",
      "board": [ {"label":"Last","main":"CAR 4 · VGK 2","tag":"Thu 6/11","mono":true,"soft":"ABC"} ],  // OPTIONAL scoreboard rows
      "links": [ {"text":"headline","src":"Outlet","url":"https://REAL-URL"} ],   // 2-3, REAL urls from search
      "notes": [ "bullet text, may use <b>bold</b>" ],     // 4-7 for teams; <=1 for NHL
      "bouts": [ {"vs":"<b>A</b> vs. <b>B</b>","wc":"LW Title · Main","title":true} ]  // UFC ONLY
    }
  ],
  "sources": "Outlet · Outlet · Outlet"
}

RULES
- Cover Bruins, Patriots, Ohio State football equally; plus an NHL section at top and a UFC section at the bottom.
- NHL: if the playoffs are active, show last result / tonight / next in "board" + series state in "ctx".
  If it's the offseason, drop "board", set pill to {"text":"Offseason","accent":true}, and cover draft/free-agency news.
- UFC: "board" = most recent completed event result + next event; "bouts" = the next event's main card
  (main event first; mark title fights with "title":true); plus 2-3 news "links".
- EVERY link.url must be a real URL you found via web_search. Never invent or guess a URL. If unsure, drop that link.
- Keep notes tight and scannable. Use &amp; for ampersands inside text. Use – / — as needed.
- Use the crest/key values exactly as listed; do not add sections or change the order.
''' % (DATE_LABEL, DATE_LONG, UPDATED)

PROMPT = (
    f"Today is {DATE_LONG} (Eastern). Build today's sports digest for a fan of the "
    "Boston Bruins, New England Patriots, and Ohio State Buckeyes, plus an NHL section "
    "at the top and a UFC section at the bottom.\n\n"
    "Use web search to gather the latest for each: NHL (playoffs if active, otherwise "
    "offseason/draft/free-agency), Bruins, Patriots, Ohio State football, and UFC "
    "(most recent completed event + the next scheduled event and its main card). "
    "Prefer recent, reputable sources (team sites, NHL.com/UFC.com/ESPN/CBS, NBC Sports "
    "Boston, Pats Pulpit, On SI, Eleven Warriors, etc.).\n\n"
    "Then output the digest as JSON.\n" + SCHEMA
)

def call_api():
    body = {
        "model": MODEL,
        "max_tokens": 8000,
        "messages": [{"role": "user", "content": PROMPT}],
        "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 14}],
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode(),
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode())

def extract_json(resp):
    text = "".join(b.get("text", "") for b in resp.get("content", []) if b.get("type") == "text").strip()
    if not text:
        raise ValueError("No text block in API response")
    if "```" in text:                       # strip any code fences
        text = text.split("```")[1]
        text = text.split("\n", 1)[1] if text.lower().startswith("json") else text
    s, e = text.find("{"), text.rfind("}")
    if s == -1 or e == -1:
        raise ValueError("No JSON object found in response")
    return json.loads(text[s:e + 1])

def main():
    if not API_KEY:
        sys.exit("ERROR: ANTHROPIC_API_KEY is not set.")
    resp = call_api()
    if resp.get("type") == "error":
        sys.exit("API error: " + json.dumps(resp.get("error", {})))
    data = extract_json(resp)
    # ensure the header fields use today's computed values regardless of model output
    data["date_label"] = DATE_LABEL
    data["date_long"] = DATE_LONG
    data["updated_label"] = UPDATED
    if not data.get("sections"):
        sys.exit("ERROR: model returned no sections; keeping previous page.")
    html = render.render(data)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote index.html ({len(html)} bytes) for {DATE_LONG} with {len(data['sections'])} sections.")

if __name__ == "__main__":
    main()
