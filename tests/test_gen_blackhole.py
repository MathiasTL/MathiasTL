import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import gen_blackhole as g


def test_renders_valid_svg():
    root = ET.fromstring(g.render())
    assert root.tag.endswith("svg")


def test_has_no_background_rect():
    # The hero must stay transparent so it blends with any GitHub theme.
    root = ET.fromstring(g.render())
    ns = "{http://www.w3.org/2000/svg}"
    top_level_rects = [el for el in root if el.tag == f"{ns}rect"]
    assert top_level_rects == []


def test_adapts_to_light_theme():
    assert "prefers-color-scheme: light" in g.render()


def test_stays_lightweight_for_readme():
    assert len(g.render().encode()) < 250_000


def test_shows_profile_info():
    svg = g.render()
    assert "Mathias Torres" in svg
    assert "AI Engineer Intern @ InSalud" in svg
