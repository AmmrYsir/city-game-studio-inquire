# Monthly Sales Model

Source: `res://scripts/controllers/game-sales.gd` (decompiled:
`decompiled/scripts/controllers/game-sales.gd`). Runs on the `month` tick for every
published game (own games, indie/contract games, remakes, gameports, DLC).

## Constants

```
MAX_ITEM_PER_ARRAY     = 24        # per-game history arrays cap
GAME_CRACKED_PUNISHMENT = 3.0      # units & fanbase ÷ 3 if the game gets cracked
```

Difficulty-scalars used (from player difficulty data): `game_retention_ratio`,
`game_sales_ratio`, `game_sales_threshold`, `cycle_boost`, `taxes_ratio`.

## Per-month unit sales (own game)

Inputs gathered per game: price (after discount), size data (`max_sales`,
`price.{average,max,limit,malus}`, `fan_ratio`, `fan_min_ratio`,
`fan_ratio_bonus`, `note_pow_factor`, `bonus_note_threshold`, `sales.times`,
`sales.pow_factor`, `max_retention`, `fan_gain`), platform userbase & cycle bonus,
theme trend, fanbase, cycle count.

```
adjusted_cycle        = cycle + saved_cycle_from_updates
platform_ratio_via_c  = (adjusted_cycle - 2) / (adjusted_cycle + 2)
max_unit_sold         = platform_unit_sold_capacity * platform_ratio_via_c
remaining_unit_sold   = max_unit_sold - units_already_sold

base_pool   = clamp(max_unit_sold, max_sales) * (trend_ratio.trend / 50)
note        = min(0.25, computed_note / 100)          # review note → 0..0.25
note       = note ** size.note_pow_factor             # genre-size-shaped
fan_ratio   = (fanbase / (cycle + 1)) * size.fan_ratio
denominator = min(1, size.sales.times * amount_of_games_on_platform ** size.sales.pow_factor)

unit_sold = ( base_pool * (1 - 1/(1 + sqrt(base_pool)/denominator)) + fan_ratio ) * note
```

The `1/(1+sqrt(base)/denom)` term is a saturation curve: the more games compete on
the platform (`amount_of_games`), the smaller the share of the base pool.

### Fanbase requirement gate

```
score_diff        = game_sales_threshold * size.bonus_note_threshold - computed_note
harder            = score_diff > 0 and fanbase > size.requirements.fanbase and self_published
required_fanbase  = size.requirements.fanbase * (1 + score_diff)  if harder
fanbase_gate      = clamp((fanbase + 1) / required_fanbase, fan_min_ratio, 1.0)
# fan_min_ratio uses fan_ratio_bonus when NOT harder
```

### Price ratio

```
r = price / size.price.max
if r >= 1: ratio = size.price.malus * size.price.limit / price
else:      ratio = size.price.max / price
ratio = max(ratio, 1.1)?  # decompiled as clamp(1.1, ratio) — see note below
```

(Argument order of the game's clamp helper is `(value, max)`-style in places;
this line clamps the ratio to at least ~1.1 at low prices — verify in bytecode
before relying on it.)

### Apply multipliers

```
unit_sold      = (unit_sold / (cycle + cycle_boost)) * price_ratio * fanbase_gate
                 * game_sales_ratio / discount_ratio
retained_users = (prev_units * size.max_retention * note / (log(cycle+10) + cycle_boost))
                 * retention_ratio * game_retention_ratio / discount_ratio
```

`discount_ratio = lerp(1, 10, sale_discount%/100) / (sales_index + 1)` — promotions
boost volume via division, and `sales_index` (accumulated sales momentum) damps it.

### Hype / marketing add-on

```
hype = retained_users * sell_bonus * 10            # sell_bonus from publisher/announcement
hype += static_sell_bonus                          # marketing campaigns (data/game.gd ratios 1.05/1.9/3.8)
hype += last_unit_sold * event_sell_bonus
hype *= marketing_manager_employee_hype_bonus
hype = int(clamp(hype, max_unit_sold)) * purchase_retention_rate
unit_sold = int(clamp(ceil(unit_sold + hype), 1, maximum_unit_sold))
```

Platform cycle bonus divides hype/units/retention when active (platform launches).

### Digital store vs physical platform split

```
ds_split       = online_capacity_ratio * clamp(size_max_sales*0.99, remaining_ds_userbase)
platform_ratio = 1 - ds_split       (when supported on both)
ds_units       = unit_sold * ds_split * ds_sales_bonus
platform_units = unit_sold * platform_split
if total > maximum_unit_sold: both scaled down proportionally
```

Online games additionally count `retained_users` as extra units and earn monthly
sub income `retained_users * monthly_price`. Server capacity caps online income.

### Piracy

If the game is cracked: units, DS units, retained users and fanbase gain all
divided by 3.

### Income

```
income = ceil(unit_sold * price * sells_ratio)      # sells_ratio = 1 - publisher royalties%
income += ceil(retained_users * monthly_price)      # online games
income += in-app purchase income
```

Then deductions in order: concurrent/publisher royalty (× concurrent_royalties),
engine royalties (if engine not owned), studio director profit bonus, taxes
(`(taxes_ratio + state_taxes) * accountant_bonus`).

## Fanbase gain

```
fanbase_threshold = clamp(fanbase / fanbase_controller_threshold, 0.5, 1) * 100
gain = unit_sold * (computed_note - fanbase_threshold) / 100 * size.fan_gain
if gain < 0:
    gain = min(fanbase * (computed_note - fanbase_threshold) / 500, unit_sold * -2.5)
    capped by fanbase_lost_threshold
gain = floor(clamp(gain, min(0, threshold - fanbase)))
```

Games scoring below the fanbase expectation actually **lose** fans.

## DLC monthly model

```
attach_rate_ratio = 1 + 2*(n_dlc-1)² / (n_dlc + 1)      # more DLCs → diminishing attach
attach_rate       = dlc.attach_rate / (100 * attach_rate_ratio)
unit_sold         = min(base_game_units, game.unit_sold_total * attach_rate * 2) in first cycle
income            = ceil(unit_sold * dlc_price)
```

## Where the numbers live

- Sizes (`max_sales`, durations, requirements, price table, fan ratios): `data/game.gd`
  → decompiled `decompiled/data/game.gd` (indie/normal/big/aaa blocks).
- Difficulty scalars (notation ratios, taxes, sales ratios): difficulty data via
  `models/player.gd` → `get_difficulty_data()` (see data/player.gd).
- Theme trends: `models/game-theme.gd` (`get_trend_by_theme`, trend/50 scaling).
- Platform userbase/cycle bonus: `controllers/platform.gd` + `data/game-platform.gd`.
