#!/usr/bin/env python3
"""Generate docs/player-guide.html — a friendly gamer-facing guide."""
import json

gt = json.load(open("extracted/game-type.json"))

# ---- build simple genre table data -------------------------------------
DESIGN = ["gameplay", "story", "characters", "graphism", "userinterface"]
DEV = ["physics", "ai", "sound", "network", "modding"]
POLISH = ["animation", "artwork", "cutscenes", "optimization", "tutoriel"]
STEPS = [("Design", DESIGN), ("Development", DEV), ("Polish", POLISH)]

# genre display name: prettify
def pretty(name):
    return name.replace("-", " ").title()

# For each genre find its TOP 3 capacities overall (the "spend most here" hint)
tops = {}
for gname, g in gt.items():
    all_caps = []
    for s in ("design", "development", "polish"):
        for k, v in g.get(s, {}).items():
            all_caps.append((k, v))
    all_caps.sort(key=lambda x: -x[1])
    tops[gname] = all_caps[:3]

rows = []
for gname, g in gt.items():
    t3 = tops[gname]
    chips = "".join(
        f'<span class="cap">{pretty(k)} <b>{v}</b></span>' for k, v in t3
    )
    cost = g.get("cost", "?")
    rows.append(f'<tr><th>{pretty(gname)}</th><td>{chips}</td><td class="num">{cost}</td></tr>')
genre_rows = "\n".join(rows)

# build platform/audience tables from game-platform.json
pl_raw = json.load(open("extracted/game-platform.json"))["list"]
aud_rows = []
for aud, label, desc in [
    ("young", "👶 Young", "Kid-friendly / family audiences"),
    ("all", "👨‍👩‍👧 All", "General audiences"),
    ("mature", "🔞 Mature", "Adult / violent themes"),
]:
    ex = sorted(p["name"] for p in pl_raw.values() if aud in (p.get("match", {}).get("excellent") or []))
    po = sorted(p["name"] for p in pl_raw.values() if aud in (p.get("match", {}).get("poor") or []))
    ex_html = " ".join(f'<span class="cap good2">{n}</span>' for n in ex[:12]) + (
        f' <span class="dim">+{len(ex)-12} more</span>' if len(ex) > 12 else "")
    po_html = " ".join(f'<span class="cap bad2">{n}</span>' for n in po[:12]) + (
        f' <span class="dim">+{len(po)-12} more</span>' if len(po) > 12 else "")
    aud_rows.append(
        f'<tr><th>{label}<br><span class="dim" style="font-weight:400">{desc}</span></th>'
        f'<td>{ex_html or "—"}</td><td>{po_html or "—"}</td></tr>')
audience_rows = "\n".join(aud_rows)

# console-families quick reference: best platforms for mature vs young
handhelds_love_young = sorted(p["name"] for p in pl_raw.values()
                              if p.get("type") == "handled" and "young" in (p.get("match", {}).get("excellent") or []))[:8]

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>City Game Studio — Player's Guide to Great Scores & Big Sales</title>
<style>
:root{
  --bg:#12182b; --panel:#1a2338; --panel2:#202b45; --ink:#e6ecfa; --dim:#93a3c4;
  --accent:#ffc94d; --accent2:#4fc3f7; --good:#57d08b; --warn:#ffb35c; --bad:#ff7b7b;
  --line:#2c3document:0;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 "Segoe UI",system-ui,sans-serif}
.wrap{max-width:960px;margin:0 auto;padding:36px 20px 90px}
header{text-align:center;margin-bottom:34px}
h1{font-size:34px;margin:0 0 8px;color:#fff}
h1 .emoji{font-size:40px}
header p{color:var(--dim);font-size:17px;max-width:640px;margin:0 auto}
h2{display:flex;align-items:center;gap:12px;font-size:24px;color:var(--accent);margin:52px 0 14px}
h2 .num{background:var(--accent);color:#1a2338;width:36px;height:36px;border-radius:12px;
        display:inline-flex;align-items:center;justify-content:center;font-size:18px;flex:0 0 auto}
h3{font-size:18px;color:var(--accent2);margin:26px 0 8px}
p{margin:10px 0}
.dim{color:var(--dim)}
.tip{background:var(--panel);border-left:5px solid var(--accent);border-radius:0 12px 12px 0;
     padding:14px 18px;margin:14px 0}
.tip b{color:var(--accent)}
.warnbox{background:#33261a;border-left:5px solid var(--warn);border-radius:0 12px 12px 0;
     padding:14px 18px;margin:14px 0}
.goodbox{background:#1a3327;border-left:5px solid var(--good);border-radius:0 12px 12px 0;
     padding:14px 18px;margin:14px 0}
.badbox{background:#331d1d;border-left:5px solid var(--bad);border-radius:0 12px 12px 0;
     padding:14px 18px;margin:14px 0}
table{border-collapse:collapse;width:100%;margin:16px 0;font-size:14.5px;background:var(--panel);border-radius:12px;overflow:hidden}
th,td{border-bottom:1px solid #26324f;padding:10px 12px;text-align:left}
thead th{background:var(--panel2);color:var(--accent2);font-size:14px}
tbody th{color:#fff;white-space:nowrap}
tbody tr:hover{background:#233052}
.num{text-align:right;font-variant-numeric:tabular-nums}
.cap{display:inline-block;background:#24365c;color:#bcd8ff;border-radius:16px;
     padding:2px 10px;margin:2px;font-size:13px}
.cap b{color:#fff}
.good2{background:#1a4a2e;color:#8ff0b6}
.bad2{background:#4a2222;color:#ff9d9d}
.bars{margin:6px 0}
.bar-row{display:flex;align-items:center;gap:10px;margin:5px 0}
.bar-row .lbl{width:130px;flex:0 0 auto;font-size:14px}
.bar-row .bar{height:16px;border-radius:8px;background:linear-gradient(90deg,#3f8fd8,#7fe0ae);min-width:4px}
.bar-row .val{font-size:13px;color:var(--dim)}
.steps{counter-reset:step;margin:18px 0}
.step{background:var(--panel);border:1px solid #2a3document;border-radius:14px;padding:16px 20px;margin:12px 0;display:flex;gap:16px;align-items:flex-start}
.step .icon{font-size:30px;flex:0 0 auto;margin-top:2px}
.step h3{margin:0 0 6px}
.size-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin:16px 0}
.size-card{background:var(--panel);border-radius:14px;padding:18px;border-top:5px solid var(--accent2)}
.size-card h3{margin:0 0 8px;color:#fff}
.size-card .big{font-size:26px;font-weight:800;color:var(--accent)}
.size-card ul{margin:8px 0 0;padding-left:18px;color:var(--dim);font-size:13.5px}
footer{margin-top:70px;text-align:center;color:var(--dim);font-size:13px;border-top:1px solid #2a3650;padding-top:16px}
.search{width:100%;padding:10px 16px;border-radius:10px;border:1px solid #2c3a5e;background:#0e1526;
        color:#fff;font-size:15px;margin:10px 0}
</style>
</head>
<body><div class="wrap">

<header>
<h1><span class="emoji">🎮</span> City Game Studio<br>Player's Guide to Great Scores &amp; Big Sales</h1>
<p>Everything below is read straight from the game's own code — no guessing, no myths.
Here's how the game actually decides your review scores and sales.</p>
</header>

<h2><span class="num">1</span>How your review score is decided</h2>
<p>When your game ships, 4 game magazines each review it. Their score comes from
four things — in order of importance:</p>

<div class="steps">

<div class="step"><div class="icon">🎯</div><div>
<h3>Pick the RIGHT genre (biggest factor)</h3>
<p>The game checks <b>what kind of game you promised</b> (genre) against
<b>the platform, the theme and the audience</b> you picked. Each pairing gets a grade:</p>
<p>
<span class="cap" style="background:#1a4a2e;color:#8ff0b6">Excellent = ×1.10</span>
<span class="cap" style="background:#1c3a52;color:#8fd0f0">Good = ×1.05</span>
<span class="cap" style="background:#3a3220;color:#ffd479">OK = ×1.00</span>
<span class="cap" style="background:#4a2222;color:#ff9d9d">Poor = ×0.85</span>
</p>
<p class="dim">Three of these grades multiply together, so one "Poor" pairing can quietly
cost you 15% of your final score. The game shows you match tips while you pick — trust them.</p>
</div></div>

<div class="step"><div class="icon">⚖️</div><div>
<h3>Balance your capacity sliders (the hidden test)</h3>
<p>Every genre has a <b>secret "shopping list"</b> of how much Gameplay, Story, Sound,
AI etc. it expects — see the table in section 2. The game doesn't just count your total
points: it checks whether you spent them <b>in the proportions the genre wants</b>.</p>
<div class="goodbox">✅ <b>Match the proportions</b> → full marks (each of the 3 dev phases is worth up to 28 points, 84 total).</div>
<div class="badbox">❌ Way over-invest in one area or starve another → up to <b>half your capacity score</b> can be lost, and reviewers will literally complain "too much X" / "not enough X".</div>
</div></div>

<div class="step"><div class="icon">⏱️</div><div>
<h3>Don't drag development on too long</h3>
<p>Dev time is worth up to <b>20 points</b> — but only if you finish inside the
"expected weeks" window for your game size. Every extra week past the maximum
<b>steals points back</b>. Speed matters, but rushing below the minimum also scores poorly.</p>
<table><thead><tr><th>Size</th><th>Healthy dev time</th></tr></thead><tbody>
<tr><th>Indie</th><td>12–24 weeks</td></tr>
<tr><th>Normal</th><td>24–56 weeks</td></tr>
<tr><th>Big</th><td>48–96 weeks</td></tr>
<tr><th>AAA</th><td>72–144 weeks</td></tr>
</tbody></table>
</div></div>

<div class="step"><div class="icon">🔁</div><div>
<h3>Don't repeat yourself</h3>
<p>Making the <b>same theme + genre combo</b> again too soon gets a "seen it before" penalty —
up to <b>−25%</b> off your score. Wait roughly <b>6–12 months</b> (depending on difficulty)
between sequels of the exact same combo, or mix in a different theme.</p>
</div></div>

</div>

<div class="tip">💡 <b>Score caps:</b> Indie games can never score above <b>85</b>,
Normal 90, Big 95, AAA 100. And a bloated custom engine can lower even that cap —
keep your engine lean for the platform.</div>

<h2><span class="num">2</span>What each genre wants (the secret shopping list)</h2>
<p>These are the <b>top 3 capacities each genre expects you to invest in most</b>
(numbers = expected points). Put your biggest sliders here and keep the rest in
rough proportion — that's what the reviewers are grading.</p>
<p class="dim">Cost = research points to unlock the genre.</p>
<input class="search" id="gsearch" type="text" placeholder="🔍 Type to filter genres… (e.g. rpg, strategy, simulation)" oninput="filterRows()">
<table id="genretable">
<thead><tr><th>Genre</th><th>Top 3 capacities to invest in</th><th class="num">Unlock cost</th></tr></thead>
<tbody>
__GENRE_ROWS__
</tbody></table>

<h2><span class="num">3</span>The four game sizes</h2>
<div class="size-grid">
<div class="size-card"><h3>🕹️ Indie</h3><div class="big">Max 85</div><ul>
<li>1 person, no producer needed</li><li>1 000 fans to unlock</li>
<li>Sells up to 100 000 copies</li><li>Price ~10, can push to 20</li>
<li>3–6 months dev time</li></ul></div>
<div class="size-card"><h3>💿 Normal</h3><div class="big">Max 90</div><ul>
<li>5 staff</li><li>10 000 fans</li><li>500 000 copies</li>
<li>Price ~20, up to 50</li><li>6–14 months</li></ul></div>
<div class="size-card"><h3>📦 Big</h3><div class="big">Max 95</div><ul>
<li>25 staff + a producer</li><li>50 000 fans</li><li>2.5M copies</li>
<li>Price ~40, up to 80</li><li>12–24 months</li></ul></div>
<div class="size-card"><h3>🏆 AAA</h3><div class="big">Max 100</div><ul>
<li>100 staff + a producer</li><li>100 000 fans</li><li>10M copies</li>
<li>Price ~60, up to 120</li><li>18–36 months</li></ul></div>
</div>
<p class="dim">Marketing campaigns scale the same way — "Full campaign" costs 350k for indie
but 5M for AAA, and multiplies your launch hype by ×3.8 vs the free campaign's ×1.05.</p>

<h2><span class="num">4</span>How monthly sales actually work</h2>

<div class="step"><div class="icon">📊</div><div>
<h3>Your review score is sales dynamite</h3>
<p>Sales don't grow linearly with the score — they explode. The game raises your
score to a huge power (7.5 for indie, up to 14 for AAA). Practically:</p>
<div class="bar-row"><div class="lbl">Score 60</div><div class="bar" style="width:6%"></div><div class="val">weak sales</div></div>
<div class="bar-row"><div class="lbl">Score 75</div><div class="bar" style="width:22%"></div><div class="val">decent</div></div>
<div class="bar-row"><div class="lbl">Score 85</div><div class="bar" style="width:55%"></div><div class="val">strong</div></div>
<div class="bar-row"><div class="lbl">Score 95</div><div class="bar" style="width:95%"></div><div class="val">blockbuster</div></div>
<p class="dim">(indie example; the gap gets even wider on bigger sizes)</p>
</div></div>

<div class="step"><div class="icon">👥</div><div>
<h3>Fanbase + freshness = units</h3>
<p>Each month you sell a slice of the platform's player base, shared with every
other game released there. Your fanbase adds direct sales, but divided by how many
months you've been out — sales <b>peak early and fade</b>. Fresh platform launches
and updates give a cycle boost.</p>
</div></div>

<div class="step"><div class="icon">🏷️</div><div>
<h3>Price sweet spot</h3>
<p>Each size has an <b>average</b> and a <b>max</b> price. Pricing near the average
gives you a healthy volume bonus; pricing <b>above max</b> triggers a penalty that
slashes volume. Cheap games sell more copies — but discounts also reduce fan gain.</p>
</div></div>

<div class="step"><div class="icon">📣</div><div>
<h3>Hype from marketing</h3>
<p>Campaigns and a good marketing manager add a one-time hype spike on top of your
monthly units — capped by platform size. Retained players (online games) keep paying
a monthly fee if your servers can handle the load.</p>
</div></div>

<div class="step"><div class="icon">😱</div><div>
<h3>Bad things that hurt</h3>
<ul>
<li><b>Piracy:</b> a cracked game sells ⅓ of what it should.</li>
<li><b>Fan loss:</b> if your score is below what your fans expect, you literally
<b>lose fans every month</b> — a flop on a big fanbase bleeds hard.</li>
<li><b>Engine royalties:</b> using someone else's engine cuts your income.</li>
<li><b>Taxes</b> take their cut every month — an accountant employee reduces them.</li>
</ul>
</div></div>

<h2><span class="num">5</span>Platforms are NOT genre-neutral</h2>

<div class="warnbox">⚠️ <b>Myth buster:</b> platforms do <b>not</b> treat all genres the same.
Every genre in the game has a secret list of consoles it works great on — and a list of
consoles where it performs poorly. A handheld-focused genre on a home console (or vice versa)
silently costs score.</div>

<p>While picking your genre, the game checks your genre against the chosen platform.
The platform has an <b>audience profile</b> — and your target audience gets graded against it:</p>

<table>
<thead><tr><th>Audience</th><th>Platforms where it's EXCELLENT (×1.10)</th><th>Platforms where it's POOR (×0.85)</th></tr></thead>
<tbody>
__AUDIENCE_ROWS__
</tbody></table>

<div class="tip">💡 <b>How to use this:</b> when a new console launches, check who it's for.
Early handhelds and kid consoles love <b>young</b>-focused games. Mid-era home consoles
are the home of <b>all-audiences</b> hits. Consoles with an adult image (many later-gen
and PC/OS platforms) reward <b>mature</b> games. Handhelds in particular usually
<span class="cap bad2">penalize mature games</span> — keep your gore on the home consoles.</div>

<div class="goodbox">✅ <b>Every genre has console preferences.</b> For example, the
Action genre is EXCELLENT on classic home consoles and handhelds of its era, but POOR
on a specific list of portables and mini-consoles. When you pick a genre, the game's
own match tips will show you the grade for the platform you've chosen — a green
"Excellent" there is real, coded information, not flavor text.</div>

<h2><span class="num">6</span>Console development &amp; ports</h2>

<div class="steps">
<div class="step"><div class="icon">📜</div><div>
<h3>Licensing costs money upfront</h3>
<p>Every console needs a <b>license</b> before you can develop for it — from about
<b>1,000</b> for ancient gen-1 machines up to <b>4,000,000</b> for the latest generation
(median around 25,000). Budget for it; the game literally checks your wallet and marks
consoles as "too expensive" if you can't afford the license.</p>
</div></div>

<div class="step"><div class="icon">🎮</div><div>
<h3>Newer console = bigger point requirement</h3>
<p>The harder the platform (CPU/GPU power), the more <b>capacity points</b> your game
needs to score well on it. A game that scored 80 on a gen-3 machine might be underwater
on a gen-8 machine if it doesn't have the points to match. When your game starts falling
behind the platform's expectations, its score caps out lower.</p>
</div></div>

<div class="step"><div class="icon">📦</div><div>
<h3>Ports: cheaper than a new game, but not free</h3>
<p>Porting a released game to another platform re-uses your original capacity points,
scaled by <b>how far the target platform is from the original</b>:</p>
<ul>
<li><b>Backwards-compatible target</b> (e.g. porting to the console that plays the
original's discs): only <b>~25%</b> extra points needed — nearly free.</li>
<li><b>Same generation, same type:</b> ~37% extra · <b>same gen, different type:</b> ~44%.</li>
<li><b>Next generation:</b> ~48–51% extra points required.</li>
</ul>
<p>The port's score also gets re-graded for the new platform — genre↔platform and
audience↔platform matches are re-checked, so a port can score <b>better or worse</b>
than the original.</p>
</div></div>

<div class="step"><div class="icon">🛡️</div><div>
<h3>Piracy &amp; copy protection</h3>
<p>Older consoles have no copy protection — your games there can get <b>cracked</b>,
and a cracked game sells one-third of what it should. Later platforms and custom
platforms (where you control <code>copy_protection</code>) protect your income.
When choosing platforms for a big release, unprotected early-era platforms are a
sales gamble.</p>
</div></div>

<div class="step"><div class="icon">🌐</div><div>
<h3>Online-capable platforms</h3>
<p>40 of the 88 platforms support online. Online enables digital-store sales,
online-game modes with monthly-subscription income — but also server costs and
capacity limits. On offline-only platforms (all retro consoles), it's physical sales only.</p>
</div></div>
</div>

<div class="tip">💡 <b>Console strategy in one line:</b> license early-era consoles
while they're cheap and their libraries are small (less competition per platform —
sales are shared among every game released there), then move your studio to each new
generation as it launches, re-porting your best back-catalog titles to
backwards-compatible machines for cheap wins.</div>

<h2><span class="num">7</span>The golden rules</h2>
<div class="tip">1️⃣ <b>Check the match tips before starting</b> — Excellent genre/platform/theme pairings are free score.</div>
<div class="tip">2️⃣ <b>Follow the genre's shopping list above</b> — balanced allocation beats dumping everything into one slider.</div>
<div class="tip">3️⃣ <b>Ship on time</b> — the last weeks of overtime cost more than they give.</div>
<div class="tip">4️⃣ <b>Never back-to-back the same combo</b> — alternate themes or wait it out.</div>
<div class="tip">5️⃣ <b>Grow into sizes</b> — a Big game with 20k fans will flop; fanbase gates sales harder than score does.</div>
<div class="tip">6️⃣ <b>A 5-point review difference is huge</b> — near release, one more polish week often pays for itself.</div>

<footer>
Made for players — every number verified from the game's actual code (see the technical
report <i>scoring-engine-report.html</i> for formulas and sources).
</footer>
</div>
<script>
function filterRows(){
  const q=document.getElementById('gsearch').value.toLowerCase();
  document.querySelectorAll('#genretable tbody tr').forEach(tr=>{
    tr.style.display=tr.textContent.toLowerCase().includes(q)?'':'none';
  });
}
</script>
</body></html>
"""

HTML = HTML.replace("__GENRE_ROWS__", genre_rows)
HTML = HTML.replace("__AUDIENCE_ROWS__", audience_rows)
# fix a couple of CSS typos from templating
HTML = HTML.replace("--line:#2c3document:0;", "--line:#2c3a5e;")
HTML = HTML.replace("border:1px solid #2a3document;", "border:1px solid #2a3a5e;")
open("docs/player-guide.html", "w", encoding="utf-8").write(HTML)
print("written docs/player-guide.html", len(HTML), "bytes")
