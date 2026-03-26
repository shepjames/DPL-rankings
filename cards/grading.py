"""
Grading ROI analysis for sports cards.

Determines whether sending a card to PSA or Beckett for professional grading
is likely to be worth the cost, based on the card's raw value, expected grade,
and current grading service fees.
"""

# ---------------------------------------------------------------------------
# Grading service fee schedules (as of early 2026)
# ---------------------------------------------------------------------------
# Each tier: (name, max_declared_value, fee, turnaround_description)
PSA_TIERS = [
    ("Value",       499,   25,  "65+ business days"),
    ("Regular",    1499,   75,  "25+ business days"),
    ("Express",    4999,  150,  "10+ business days"),
    ("Super Exp.", 9999,  300,  "5+ business days"),
    ("Walk-Through", None, 600, "1-3 business days"),
]

BECKETT_TIERS = [
    ("Economy",     499,   22,  "55+ business days"),
    ("Standard",   2499,   40,  "25+ business days"),
    ("Expedited",  4999,  100,  "15+ business days"),
    ("Premium",    9999,  250,  "5+ business days"),
]

# ---------------------------------------------------------------------------
# Grade-based value multipliers
# ---------------------------------------------------------------------------
# These rough multipliers represent how much more a graded card is typically
# worth compared to its raw (ungraded) value.  Real-world multipliers vary
# widely by card; these are conservative middle-of-the-road estimates.

GRADE_MULTIPLIERS = {
    10:   5.0,    # Gem Mint — significant premium
    9.5:  3.5,    # Mint+
    9:    2.5,    # Mint
    8.5:  2.0,
    8:    1.7,    # Near Mint–Mint
    7.5:  1.4,
    7:    1.2,    # Near Mint
    6.5:  1.1,
    6:    1.0,    # Excellent–Near Mint (roughly breaks even)
    5:    0.85,
    4:    0.7,
    3:    0.55,
    2:    0.4,
    1:    0.3,
}


def _nearest_grade(grade: float) -> float:
    """Snap to the closest grade we have a multiplier for."""
    return min(GRADE_MULTIPLIERS, key=lambda g: abs(g - grade))


def estimated_graded_value(raw_value: float, expected_grade: float) -> float:
    """Estimate what a card would be worth after receiving a given grade."""
    mult = GRADE_MULTIPLIERS[_nearest_grade(expected_grade)]
    return round(raw_value * mult, 2)


def best_grading_tier(raw_value: float, tiers: list[tuple]) -> tuple | None:
    """Pick the cheapest tier whose declared-value cap covers the card."""
    for name, cap, fee, turnaround in tiers:
        if cap is None or raw_value <= cap:
            return (name, fee, turnaround)
    return tiers[-1][0], tiers[-1][2], tiers[-1][3]


def grading_analysis(raw_value: float, expected_grade: float) -> dict:
    """
    Full grading ROI analysis for a single card.

    Returns a dict with estimated graded value, costs, and profit/loss
    for both PSA and Beckett.
    """
    graded_val = estimated_graded_value(raw_value, expected_grade)
    grade_used = _nearest_grade(expected_grade)

    results = {
        "raw_value": raw_value,
        "expected_grade": expected_grade,
        "grade_used_for_calc": grade_used,
        "multiplier": GRADE_MULTIPLIERS[grade_used],
        "estimated_graded_value": graded_val,
        "services": {},
    }

    for label, tiers in [("PSA", PSA_TIERS), ("Beckett", BECKETT_TIERS)]:
        tier_name, fee, turnaround = best_grading_tier(raw_value, tiers)
        profit = round(graded_val - raw_value - fee, 2)
        results["services"][label] = {
            "tier": tier_name,
            "fee": fee,
            "turnaround": turnaround,
            "profit": profit,
            "worth_it": profit > 0,
        }

    return results


def format_analysis(analysis: dict) -> str:
    """Pretty-print the grading analysis."""
    lines = []
    lines.append("=" * 60)
    lines.append("  GRADING ANALYSIS")
    lines.append("=" * 60)
    lines.append(f"  Raw value:              ${analysis['raw_value']:,.2f}")
    lines.append(f"  Expected grade:         {analysis['expected_grade']}")
    lines.append(f"  Value multiplier:       {analysis['multiplier']}x (grade {analysis['grade_used_for_calc']})")
    lines.append(f"  Estimated graded value: ${analysis['estimated_graded_value']:,.2f}")
    lines.append("-" * 60)

    for svc, info in analysis["services"].items():
        verdict = "YES — worth grading!" if info["worth_it"] else "NO — not worth the cost"
        lines.append(f"\n  {svc} ({info['tier']} tier)")
        lines.append(f"    Fee:        ${info['fee']:,.2f}")
        lines.append(f"    Turnaround: {info['turnaround']}")
        lines.append(f"    Net profit: ${info['profit']:,.2f}")
        lines.append(f"    Verdict:    {verdict}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_batch_analysis(cards_with_analysis: list[tuple[dict, dict]]) -> str:
    """Format a summary table of grading analysis for multiple cards."""
    lines = []
    lines.append("=" * 90)
    lines.append("  GRADING CANDIDATES — SUMMARY")
    lines.append("=" * 90)
    header = f"  {'Player':<22} {'Year':<6} {'Raw $':>8} {'Grade':>5} {'Graded $':>9} {'PSA':>10} {'Beckett':>10}"
    lines.append(header)
    lines.append("-" * 90)

    worth_grading = []
    not_worth = []

    for card, analysis in cards_with_analysis:
        psa = analysis["services"]["PSA"]
        beck = analysis["services"]["Beckett"]
        psa_str = f"${psa['profit']:+,.0f}" if psa["worth_it"] else "skip"
        beck_str = f"${beck['profit']:+,.0f}" if beck["worth_it"] else "skip"

        row = (
            f"  {card['player']:<22} {card['year']:<6} "
            f"${card['raw_value']:>7,.2f} {analysis['expected_grade']:>5} "
            f"${analysis['estimated_graded_value']:>8,.2f} "
            f"{psa_str:>10} {beck_str:>10}"
        )
        if psa["worth_it"] or beck["worth_it"]:
            worth_grading.append(row)
        else:
            not_worth.append(row)

    if worth_grading:
        lines.append("  *** WORTH GRADING ***")
        lines.extend(worth_grading)
    if not_worth:
        if worth_grading:
            lines.append("")
        lines.append("  --- Not worth grading at this time ---")
        lines.extend(not_worth)

    lines.append("=" * 90)
    return "\n".join(lines)
