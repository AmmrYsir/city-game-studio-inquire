# Review & Score System

Source of truth: `res://scripts/controllers/game.gd` (decompiled, in this workspace
under `decompiled/scripts/controllers/game.gd`). Constants below are confirmed from
the bytecode. Difficulty-scaled values (`notation_ratios.*`) come from the player
model's difficulty data — see docs/mechanics/difficulty.md.

## Pipeline (func `compute_notation`)

When a game finishes development, the final score is computed in this order:

```
1. max_note        = compute_max_note(size.max_note, ...)          # engine penalty
2. capacity note   = compute_note_from_capacities(game)            # absolute_note (0..84)
3. absolute_note  *= theme/type/platform match ratios
4. absolute_note   = clamp(absolute_note * duration_note / 20, 1.0, max_note)
5. absolute_note  *= platform library ratio
6. absolute_note  *= combo repeat penalty
7. computed_note   = mean of 4 magazine notes (±10% jitter each)
```

## 1. Engine penalty — `compute_max_note`

```
platform_size_ratio      = engine size ratio for the game's size
required_capacities      = platform GPU requirement + CPU requirement
used_capacities          = game engine's CPU + GPU feature costs
note_ratio = nearest_po2(platform_size_ratio * (1 - used/required),
                         -platform_size_ratio/4, platform_size_ratio)
max_note = size.max_note - note_ratio
```

Feedback: note_ratio > 1.5 → "engine too heavy" BAD review; < 0.5 → GOOD.

`nearest_po2(x, min, max)` here is a clamp-style helper (name borrowed from the
engine's function table; the game's utils re-map it) — semantically: clamp(x, min, max).

## 2. Capacity points — `compute_note_from_capacities`

Three phases, each scored by `compute_capacity_note(step, keys, game, max_note=28)`:

- `design` (capacities: gameplay, story, graphism, sound, ... per capacity model)
- `development`
- `polish`

Per capacity within a phase (`capacity_max_note = 28`, split evenly across the
capacities the game actually has):

```
note_per_items  = 28 / n_keys
game_data_value = game_data[key]
expected_value  = gametype_model.get_average_step_capacity(type_list, step, key)

# normalized shares
game_share     = game_data[key]  / sum(game values in phase)
expected_share = expected[key]   / sum(expected values in phase)

delta = |expected_share - game_share| * capacity_delta_time      # difficulty value
current_note = note_per_items * (expected_share - clamp(delta,0,expected_share)) / expected_share

# qualitative feedback on absolute values
|game - expected| > 20  -> "too much X"  (BAD feedback)
|game - expected| <= 5  -> "good X"      (GOOD feedback)

capacity_note = sum of current_note across keys
```

So the engine rewards matching the **genre's expected distribution** of points
between capacities, not just raw totals.

### Inter-capacity rebalance — `compute_capacities_note_ratio`

```
total_expected = Σ expected;  total_value = Σ actual points
ratio = clamp(0.1 + (share_actual / share_expected), 1.0, ...)
# (0.1 offset then clamp lower-bound 1.0; exact clamp order in bytecode)
note *= lerp(0.5, 1.0, ratio)
```

Feedback thresholds: ratio <= 0.6 → "not enough X"; >= 0.8 → "good X".
Ratios `0.6`/`0.8` are hardcoded.

### Required points baseline — `get_number_of_points_to_produce`

```
week_productivity = date_model.get_week_duration() / staff_controller.minimum_delta
productivity      = 1.15 if size requires a producer else 1.0
ideal_duration    = (size.duration_in_week.max + min) / 2
avg_emp_prod      = 0.4671 * productivity * week_productivity
required_points   = ideal_duration * size.requirements.staff * avg_emp_prod
                    * notation_ratios.point_to_produce_ratio
```

The magic constant `0.4671` is the per-employee weekly point productivity
(hardcoded, confirmed).

## 3. Theme/type/platform matching — `compute_ratio_from_theme_type_platform`

Three multiplicative match ratios from `match_utils.compute_match`:

- `type_list` vs platform's preferred genres
- theme's `match` list vs the chosen genre(s)
- platform's `match` list vs the chosen target audience

(Exact per-ratio scales live in `scripts/utils/match-utils.gd` and the data tables
`data/game-platform.gd` / `data/game-theme.gd` — see docs/mechanics/data-tables.md.)

## 4. Duration factor — `compute_note_ratio_based_on_duration`

Constants: `GAME_DURATION_MAX_NOTE = 20`, `GAME_DURATION_MIN_NOTE = 5.0`.

```
min_weeks = size.duration_in_week.min * week_in_month_ratio
max_weeks = size.duration_in_week.max * week_in_month_ratio
note = duration * 20 / min_weeks
if duration > max_weeks:
    note = 20 - (duration - max_weeks) * 20 / min_weeks
duration_note = clamp(note, 5.0, 20)
```

Overshooting the max duration *reduces* the score linearly.

## 5. Platform library — `compute_note_from_platform`

Compares your total capacity points vs the points of the best same-size/same-genre
game already on the platform (min over candidates, floor at your own baseline):

```
rival_points = min(rival.total_capacities_points, your_baseline_required_points)
note_ratio   = clamp(your_total_points / rival_points, capacity_min_ratio, max_bonus)
absolute_note *= lerp(size.platform_note_min_ratio, 1.0, note_ratio)
```

Feedback: ratio >= 1.0 → "better than <game>" GOOD; <= 0.95 → BAD.

## 6. Combo repetition

```
months_since_last = diff_in_month(now, last game with same theme+genre combo)
last_combos_ratio = clamp(min_delay_ratio(months_since_last), 0.75, 1.0)
absolute_note *= last_combos_ratio
```

Feedback: ratio >= 1.0 GOOD ("fresh idea"), <= 0.9 BAD ("repetitive").
`notation_ratios.min_delay` (difficulty data) sets the cooldown months.

## 7. Magazine notes — `compute_relative_notes`

`AMOUNT_OF_MAGAZINES = 4`.

```
if forced_score > 0:   # debug/publisher-forced
    notes = [s, s, s, s]
else:
    if absolute_note > 100: absolute_note -= absolute_note % 10   # round down to tens
    for each of 4 magazines:
        note = int(absolute_note * random(0.9, 1.1))
        if note > 100: note -= note % 10
computed_note = int(sum(notes) / 4)
```

So the four magazine scores are the absolute note each ±10%, floored to
multiples of 10 when above 100. `computed_note` is what feeds sales, fanbase and
awards; `absolute_note` is pre-jitter.

## Note scale

The A–E quality icons (`res://theme/icon/quali-score/`) map to ranges of the
0–100+ scale; exact cutoffs are applied in UI code (`magazine-review.gd`), see
docs/mechanics/ui-review-presentation.md (TODO).
