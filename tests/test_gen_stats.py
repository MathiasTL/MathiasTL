import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import gen_stats as g


def _day(date, count, level="NONE"):
    return {"date": date, "contributionCount": count, "contributionLevel": level}


def test_streaks_counts_current_and_longest():
    days = [_day("2026-01-01", 1), _day("2026-01-02", 2), _day("2026-01-03", 0),
            _day("2026-01-04", 3), _day("2026-01-05", 1), _day("2026-01-06", 4)]
    assert g.streaks(days) == (3, 3)


def test_current_streak_survives_empty_today():
    days = [_day("2026-01-01", 1), _day("2026-01-02", 1), _day("2026-01-03", 0)]
    assert g.streaks(days, today="2026-01-03") == (2, 2)


def test_top_languages_ignores_noise_and_normalizes():
    repos = [{"languages": {"edges": [
        {"size": 300, "node": {"name": "Python"}},
        {"size": 100, "node": {"name": "TypeScript"}},
        {"size": 9999, "node": {"name": "Jupyter Notebook"}},
    ]}}]
    langs = g.top_languages(repos)
    assert [n for n, _ in langs] == ["Python", "TypeScript"]
    assert abs(sum(s for _, s in langs) - 1) < 1e-9


def test_cards_are_valid_svg():
    days = [_day("2026-01-0%d" % i, i % 3, "FIRST_QUARTILE" if i % 3 else "NONE") for i in range(1, 8)]
    ET.fromstring(g.render_activity(days, 10, 2, 3))
    ET.fromstring(g.render_languages([("Python", 0.6), ("TypeScript", 0.4)]))
