#!/usr/bin/env python3
"""One-time full rebuild of docs/player-guide.html with ALL data inlined.
After this runs, the HTML is the source of truth — edit it directly."""
import json

gt = json.load(open("extracted/game-type.json"))
pl = json.load(open("extracted/game-platform.json"))["list"]

def pretty(s):
    return s.replace("-", " ").title()

# ---------- genre matrix (all 15 capacities) ----------
STEPS = [("design", "Design"), ("development", "Development"), ("polish", "Polish")]
cap_keys = {}
for s, _ in STEPS:
    keys = []
    for g in gt.values():
        for k in g.get(s, {}):
            if k not in keys: keys.append(k)
    cap_keys[s] = keys

mhead = '<th class="rot"><div>Genre</div></th>'
for s, label in STEPS:
    mhead += f'<th class="grp" colspan="{len(cap_keys[s])}">{label}</th>'
mhead2 = "<th>Genre</th>" + "".join(
    f'<th class="rot"><div>{pretty(k)}</div></th>' for s, _ in STEPS for k in cap_keys[s])

mrows = []
for gname, g in gt.items():
    cells = ""
    for s, _ in STEPS:
        for k in cap_keys[s]:
            v = g.get(s, {}).get(k)
            if v is None:
                cells += '<td class="dim">–</td>'
            else:
                cells += f'<td><span class="hv" style="--v:{min(100,int(v))}">{v}</span></td>'
    mrows.append(f'<tr><th>{pretty(gname)}</th>{cells}</tr>')
genre_matrix = f"<thead><tr>{mhead}</tr><tr>{mhead2}</tr></thead><tbody>" + "\n".join(mrows) + "</tbody>"

# ---------- platform table (ALL 88) ----------
GRADE = {"excellent": "E", "good": "G", "ok": "O", "poor": "P"}
TYPE_LABEL = {"home": "🏠 Home", "handled": "🎒 Handheld", "pc": "🖥 PC", "os": "💻 OS", "accessory": "🔌 Accessory"}

prows = []
for pid, p in sorted(pl.items(), key=lambda kv: (kv[1].get("generation", 0), kv[0])):
    m = p.get("match", {})
    def cell(aud):
        for grade in ("excellent", "good", "ok", "poor"):
            if aud in (m.get(grade) or []):
                return f'<span class="g {grade[0]}">{GRADE[grade]}</span>'
        return '<span class="dim">·</span>'
    online = "🌐" if p.get("online", {}).get("compatible") else "—"
    prot = "✔" if p.get("copy_protection") else '<span class="dim">✘</span>'
    lic = p.get("cost", {}).get("license", "?")
    prows.append(
        f'<tr><th>{p["name"]}</th><td class="num">{p.get("generation","?")}</td>'
        f'<td>{TYPE_LABEL.get(p.get("type"), p.get("type"))}</td>'
        f'<td class="ctr">{online}</td><td class="ctr">{prot}</td>'
        f'<td class="num">{lic:,}</td>'
        f'<td class="ctr">{cell("young")}</td><td class="ctr">{cell("all")}</td><td class="ctr">{cell("mature")}</td></tr>')
platform_table = ("<thead><tr><th>Platform</th><th class='num'>Gen</th><th>Type</th><th>Online</th>"
                  "<th>Anti-piracy</th><th class='num'>License</th><th>👶 Young</th><th>👨‍👩‍👧 All</th>"
                  "<th>🔞 Mature</th></tr></thead><tbody>" + "\n".join(prows) + "</tbody>")

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>City Game Studio — Player's Guide to Great Scores & Big Sales</title>
<style>
:root{
  --bg:#12182b; --panel:#1a2338; --panel2:#202b45; --ink:#e6ecfa; --dim:#93a3c4;
  --accent:#ffc94d; --accent2:#4fc3f7; --good:#57d08b; --warn:#ffb35c; --bad:#ff7b7b;
  --line:#2c3a5e;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 "Segoe UI",system-ui,sans-serif}
.wrap{max-width:1000px;margin:0 auto;padding:36px 20px 90px}
header{text-align:center;margin-bottom:34px}
h1{font-size:34px;margin:0 0 8px;color:#fff}
header p{color:var(--dim);font-size:17px;max-width:640px;margin:0 auto}
h2{display:flex;align-items:center;gap:12px;font-size:24px;color:var(--accent);margin:52px 0 14px}
h2 .num{background:var(--accent);color:#1a2338;width:36px;height:36px;border-radius:12px;
        display:inline-flex;align-items:center;justify-content:center;font-size:18px;flex:0 0 auto}
h3{font-size:18px;color:var(--accent2);margin:26px 0 8px}
.dim{color:var(--dim)}
.tip{background:var(--panel);border-left:5px solid var(--accent);border-radius:0 12px 12px 0;padding:14px 18px;margin:14px 0}
.warnbox{background:#33261a;border-left:5px solid var(--warn);border-radius:0 12px 12px 0;padding:14px 18px;margin:14px 0}
.goodbox{background:#1a3327;border-left:5px solid var(--good);border-radius:0 12px 12px 0;padding:14px 18px;margin:14px 0}
.badbox{background:#331d1d;border-left:5px solid var(--bad);border-radius:0 12px 12px 0;padding:14px 18px;margin:14px 0}
table{border-collapse:collapse;width:100%;margin:16px 0;font-size:14px;background:var(--panel)}
th,td{border-bottom:1px solid #26324f;padding:8px 10px;text-align:left}
thead th{background:var(--panel2);color:var(--accent2);font-size:13.5px}
tbody th{color:#fff;white-space:nowrap}
tbody tr:hover{background:#233052}
.num{text-align:right;font-variant-numeric:tabular-nums}
.ctr{text-align:center}
.cap{display:inline-block;background:#24365c;color:#bcd8ff;border-radius:16px;padding:2px 10px;margin:2px;font-size:13px}
.cap b{color:#fff}
.g{display:inline-block;width:22px;height:22px;line-height:22px;border-radius:6px;font-weight:800;font-size:12px;color:#fff}
.g.e{background:#1a6a3e}.g.g{background:#245e8a}.g.o{background:#6b5a20}.g.p{background:#7a2e2e}
.step{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 20px;margin:12px 0;display:flex;gap:16px;align-items:flex-start}
.step .icon{font-size:30px;flex:0 0 auto;margin-top:2px}
.step h3{margin:0 0 6px}
.bar-row{display:flex;align-items:center;gap:10px;margin:5px 0}
.bar-row .lbl{width:130px;flex:0 0 auto;font-size:14px}
.bar-row .bar{height:16px;border-radius:8px;background:linear-gradient(90deg,#3f8fd8,#7fe0ae)}
.bar-row .val{font-size:13px;color:var(--dim)}
/* matrix */
.matrixwrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px}
table.matrix{font-size:11px;margin:0;background:var(--panel)}
.matrix td,.matrix th{padding:3px 6px;text-align:center;border-right:1px solid #202b45}
.matrix tbody th{text-align:left}
.matrix .grp{text-align:center;background:#16223c;color:var(--accent2);border-bottom:1px solid var(--line)}
.hv{display:inline-block;min-width:30px;padding:2px 3px;border-radius:4px;color:#eaf4ff;
    background:rgb(42,111,181);opacity:calc(0.15 + var(--v)*0.0085)}
.rot{height:88px;white-space:nowrap}
.rot div{transform:rotate(-55deg) translate(6px,-2px);transform-origin:bottom left;width:14px}
.search{width:100%;padding:10px 16px;border-radius:10px;border:1px solid var(--line);background:#0e1526;color:#fff;font-size:15px;margin:10px 0}
footer{margin-top:70px;text-align:center;color:var(--dim);font-size:13px;border-top:1px solid #2a3650;padding-top:16px}
</style>
</head>
<body><div class="wrap">

<header>
<h1>🎮 City Game Studio<br>Player's Guide to Great Scores &amp; Big Sales</h1>
<p>Everything here is read straight from the game's own code — no guessing, no myths.</p>
</header>

<h2><span class="num">1</span>How your review score is decided</h2>
<p>When your game ships, 4 magazines review it. Their score comes from four things:</p>

<div class="step"><div class="icon">🎯</div><div><h3>Pick the RIGHT genre + platform + audience</h3>
<p>The game grades three pairings and multiplies them:
<span class="cap" style="background:#1a4a2e;color:#8ff0b6">Excellent ×1.10</span>
<span class="cap" style="background:#1c3a52;color:#8fd0f0">Good ×1.05</span>
<span class="cap" style="background:#3a3220;color:#ffd479">OK ×1.00</span>
<span class="cap" style="background:#4a2222;color:#ff9d9d">Poor ×0.85</span></p>
<p class="dim">genre↔platform · theme↔genre · platform↔target audience. One "Poor" quietly costs 15% of your score. The in-game match tips are real coded data — trust them.</p>
</div></div>

<div class="step"><div class="icon">⚖️</div><div><h3>Balance your capacity sliders</h3>
<p>Every genre has a secret "shopping list" (section 2). Reviewers grade the
<b>proportions</b> of your spending, not the total. Matching proportions = full marks
(28 points × 3 phases). Lopsided allocation can cost <b>half</b> the capacity score and
triggers "too much X" / "not enough X" complaints.</p></div></div>

<div class="step"><div class="icon">⏱️</div><div><h3>Ship on time</h3>
<p>Dev time is worth up to 20 points, only inside the healthy window.
Indie 12–24 wks · Normal 24–56 · Big 48–96 · AAA 72–144. Every week past the max
steals points back.</p></div></div>

<div class="step"><div class="icon">🔁</div><div><h3>Don't repeat yourself</h3>
<p>Same theme+genre combo within ~6–12 months = up to −25% score.</p></div></div>

<div class="tip">💡 <b>Score caps:</b> Indie max <b>85</b> · Normal 90 · Big 95 · AAA 100.
A bloated engine lowers the cap further.</div>

<h2><span class="num">2</span>What each genre wants — full matrix</h2>
<p>Numbers = expected points per capacity. <b>Match the ratios between columns</b>;
darker = more expected. "–" = the genre doesn't use that capacity at all, so any
points spent there are wasted (and hurt your proportion score).</p>
<input class="search" id="gsearch" type="text" placeholder="🔍 Filter genres… (e.g. rpg, racing, strategy)" oninput="filterTable('gsearch','genretable')">
<div class="matrixwrap">
<table class="matrix" id="genretable">
__GENRE_MATRIX__
</table>
</div>

<h2><span class="num">3</span>Pricing — the sweet spot is bigger than you think</h2>

<div class="step"><div class="icon">🏷️</div><div>
<h3>How price actually affects sales</h3>
<p>The game compares your price to your size's <b>max</b> price:</p>
<ul>
<li><b>At or below max price</b> → volume ratio ≈ <span class="mono">max_price / your_price</span>.
Halving the price roughly <b>doubles</b> copies sold.</li>
<li><b>Above max price</b> → a penalty kicks in: <span class="mono">malus × limit / price</span>.
The malus (0.5–0.8) is brutal — pricing AAA at 150 instead of 120 costs you ~35% volume.</li>
<li><b>Recommendation:</b> price at the size's <b>average</b> — near-max revenue
without the malus. Only go below average for fanbase farming or when a game underperformed.</li>
</ul>
</div></div>

<table>
<thead><tr><th>Size</th><th class="num">Average price</th><th class="num">Max price</th><th class="num">Hard limit</th><th class="num">Overprice penalty (malus)</th></tr></thead>
<tbody>
<tr><th>🕹️ Indie</th><td class="num">10</td><td class="num">15</td><td class="num">20</td><td class="num">0.5 (harshest)</td></tr>
<tr><th>💿 Normal</th><td class="num">20</td><td class="num">35</td><td class="num">50</td><td class="num">0.6</td></tr>
<tr><th>📦 Big</th><td class="num">40</td><td class="num">60</td><td class="num">80</td><td class="num">0.7</td></tr>
<tr><th>🏆 AAA</th><td class="num">60</td><td class="num">80</td><td class="num">120</td><td class="num">0.8</td></tr>
</tbody></table>
<div class="tip">💡 Discounts multiply volume up to ×10 at −90% off, and sales momentum
(sales index) slightly damps further discounts — timing a sale late in a game's life
gives it a strong second wind.</div>

<h2><span class="num">4</span>Marketing &amp; hype</h2>

<div class="step"><div class="icon">📣</div><div>
<h3>Where hype comes from</h3>
<ul>
<li><b>Marketing campaigns</b> (run during the window before release): the campaign's
<b>ratio multiplies your last month's unit sales into extra launch hype</b>.</li>
<li><b>Publisher / announcement hype</b>: self-published games start at 0.5 hype ratio;
using a publisher or a good announcement pushes it up to 4×.</li>
<li><b>Events &amp; conventions</b> add a static bonus, and your last month's sales add
proportional hype.</li>
<li>A hired <b>Marketing Manager</b> multiplies all of it by their bonus.</li>
</ul>
</div></div>

<table>
<thead><tr><th>Campaign</th><th class="num">Hype ratio</th><th class="num">Indie cost</th><th class="num">Normal</th><th class="num">Big</th><th class="num">AAA</th><th class="num">Duration (wks)</th></tr></thead>
<tbody>
<tr><th>Free (no cost)</th><td class="num">×1.05</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">12</td></tr>
<tr><th>Demo</th><td class="num">×1.9</td><td class="num">50 000</td><td class="num">125 000</td><td class="num">250 000</td><td class="num">500 000</td><td class="num">16</td></tr>
<tr><th>Full</th><td class="num">×3.8</td><td class="num">350 000</td><td class="num">900 000</td><td class="num">2 000 000</td><td class="num">5 000 000</td><td class="num">32–64</td></tr>
</tbody></table>
<div class="warnbox">⚠️ Hype is <b>capped by the platform's size</b> — pumping millions into
a Full campaign for an indie game on a tiny platform wastes money. Match the campaign to
the platform's userbase.</div>

<h2><span class="num">5</span>Sales month by month</h2>
<div class="step"><div class="icon">📊</div><div><h3>Review score is sales dynamite</h3>
<p>The score is raised to a huge power (7.5 indie … 14 AAA):</p>
<div class="bar-row"><div class="lbl">Score 60</div><div class="bar" style="width:6%"></div><div class="val">weak</div></div>
<div class="bar-row"><div class="lbl">Score 75</div><div class="bar" style="width:22%"></div><div class="val">decent</div></div>
<div class="bar-row"><div class="lbl">Score 85</div><div class="bar" style="width:55%"></div><div class="val">strong</div></div>
<div class="bar-row"><div class="lbl">Score 95</div><div class="bar" style="width:95%"></div><div class="val">blockbuster</div></div>
</div></div>
<div class="step"><div class="icon">👥</div><div><h3>Fanbase + freshness = units</h3>
<p>You sell a share of the platform's userbase, split with every other game released
there. Fanbase adds direct sales; both fade as months pass. Games scoring below the
fans' expectation <b>lose fans monthly</b> instead.</p></div></div>
<div class="step"><div class="icon">😱</div><div><h3>Bad things</h3>
<ul><li><b>Piracy</b>: cracked games sell ⅓ (retro platforms lack protection).</li>
<li><b>Engine royalties</b> if using someone else's engine; <b>publisher royalties</b> if not self-published.</li>
<li><b>Taxes</b> monthly — an accountant employee reduces them.</li></ul></div></div>

<h2><span class="num">6</span>Platforms &amp; consoles — full reference</h2>

<div class="warnbox">⚠️ Platforms are <b>not</b> genre-neutral. Every genre has secret
console preferences (Excellent/Poor lists), and every platform grades your
<b>target audience</b>. Below: all 88 platforms with their audience grades.</div>

<p><span class="g e">E</span> Excellent ×1.10 · <span class="g g">G</span> Good ×1.05 ·
<span class="g o">O</span> OK ×1.00 · <span class="g p">P</span> Poor ×0.85 ·
<span class="dim">·</span> neutral · Anti-piracy ✔ = protected, ✘ = can be cracked (⅓ sales)</p>

<div class="matrixwrap">
<table class="matrix" id="plat_table" style="font-size:13px">
__PLATFORM_TABLE__
</table>
</div>

<div class="tip">💡 <b>Console strategy:</b> license old consoles while cheap — fewer
competing games means a bigger sales share. Move to each new generation early
(harder platforms demand more capacity points). Port your back catalog to
backwards-compatible machines (~25% extra points = nearly free money). Keep mature
games off handhelds; they almost universally penalize them.</div>

<footer>
Every number verified from the game's actual code. Technical companion:
<i>scoring-engine-report.html</i>. Generated once from extracted data;
now maintained directly as HTML.
</footer>
</div>
<script>
function filterTable(inputId, tableId){
  const q=document.getElementById(inputId).value.toLowerCase();
  document.querySelectorAll('#'+tableId+' tbody tr').forEach(tr=>{
    tr.style.display=tr.textContent.toLowerCase().includes(q)?'':'none';
  });
}
</script>
</body></html>
"""

HTML = HTML.replace("__GENRE_MATRIX__", genre_matrix).replace("__PLATFORM_TABLE__", platform_table)
open("docs/player-guide.html", "w", encoding="utf-8").write(HTML)
print("written docs/player-guide.html", len(HTML), "bytes")
