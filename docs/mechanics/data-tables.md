# Game Size Data Table (data/game.gd)

Confirmed from decompiled `decompiled/data/game.gd` (all values verbatim).
Sizes: **indie / normal / big / aaa**.

| Field | indie | normal | big | aaa |
|---|---|---|---|---|
| index | 0 | 1 | 2 | 3 |
| xp_game_type | 44 | 96 | 176 | 304 |
| duration_in_week min–max | 12–24 | 24–56 | 48–96 | 72–144 |
| cycle_step | 2 | 1.667 | 1.334 | 1 |
| cost_per_week | 300 | 5 000 | 25 000 | 50 000 |
| requirements.producer | 0 | 0 | 1 | 1 |
| requirements.fanbase | 1 000 | 10 000 | 50 000 | 100 000 |
| requirements.staff | 1 | 5 | 25 | 100 |
| extra_week_cost_factor | 6 | 4 | 2 | 1.5 |
| extra_week_efficiency | 0.75 | 0.8 | 0.85 | 0.9 |
| xp_ratio | 0.015 | 0.03483 | 0.0850 | 0.15217 |
| price.average / max / limit / malus | 10/15/20/0.5 | 20/35/50/0.6 | 40/60/80/0.7 | 60/80/120/0.8 |
| sales.pow_factor / times / max_cycle | 1.1 / 4 / 12 | 1.1 / 8 / 18 | 1.1 / 16 / 24 | 1.1 / 32 / 48 |
| platform_generation_requirement | 0.7665 | 6.587 | 32.935 | 131.74 |
| platform_note_min_ratio | 0.5 | 0.3 | 0.2 | 0.15 |
| **max_sales** | 100 000 | 500 000 | 2 500 000 | 10 000 000 |
| remake_review_ease | 10 | 20 | 40 | 80 |
| **max_note** | 85 | 90 | 95 | 100 |
| bonus_note_threshold | 95 | 95 | 90 | 90 |
| note_pow_factor | 7.5 | 11.5 | 12.5 | 14 |
| fan_ratio | 0.55 | 0.65 | 0.85 | 1.1 |
| fan_min_ratio | 0.0593 | 0.0393 | 0.0293 | 0.0193 |
| fan_ratio_bonus | 5 | 7 | 14 | 20 |
| fan_gain | 0.008 | 0.01 | 0.0125 | 0.015625 |
| max_retention | 0.19125 | 0.21654 | 0.23336 | 0.43336 |
| theme_xp | 10 | 20 | 40 | 80 |
| limit | 5 000 | 25 000 | 2 250 000 | 8 437 500 |
| contract_ratio | 4 | 6 | 9 | 12 |

## Marketing campaigns (per size)

| Campaign | ratio | indie cost | normal | big | aaa |
|---|---|---|---|---|---|
| No cost | 1.05 | 0 | 0 | 0 | 0 |
| Demo | 1.9 | 50 000 | 125 000 | 250 000 | 500 000 |
| Full | 3.8 | 350 000 | 900 000 | 2 000 000 | 5 000 000 |

Marketing duration (weeks): indie 12, normal 16, big 32, aaa 64.

## score.gd companion table (`data/score.gd`)

```
game.size cost points: indie 50, normal 100, big 200, aaa 500
contract points by size: indie 5, normal 10, big 20, aaa 50
game-type 5 · platform 15 · game-engine 3 · digital-store 0.1
game-port 150 · convention 0.0001 · custom-platform 15
```

## post_mortem amount arrays

Weight tables used to pick post-mortem review paragraphs (index = rating bucket?):
indie `[0,10,20,40,20]`, normal `[0,10,10,20,40,30]`, big `[0,5,5,10,30,50,30]`,
aaa `[0,5,5,10,30,50,40,10]`.
