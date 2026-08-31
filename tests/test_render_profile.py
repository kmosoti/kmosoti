from __future__ import annotations

import re
import struct
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import render_profile as renderer


def visible_words(markdown: str) -> list[str]:
    text = re.sub(r"<!--.*?-->", " ", markdown, flags=re.DOTALL)
    text = re.sub(
        r'<img\b[^>]*\balt="([^"]*)"[^>]*>',
        lambda match: " " + match.group(1) + " ",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"!?\[([^]]+)]\([^)]+\)", r"\1", text)
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9’'./+-]*", text)


class ManifestTests(unittest.TestCase):
    def test_current_manifest_has_the_exact_project_contract(self) -> None:
        profile = renderer.load_profile()
        self.assertEqual(
            [project.name for project in profile.projects], renderer.EXPECTED_PROJECTS
        )
        self.assertEqual(len({project.id for project in profile.projects}), 5)

    def test_unknown_manifest_fields_fail_loudly(self) -> None:
        source = renderer.MANIFEST.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.toml"
            path.write_text(
                source.replace("schema_version = 1", "schema_version = 1\nextra = true")
            )
            with self.assertRaisesRegex(ValueError, "unknown extra"):
                renderer.load_profile(path)

    def test_missing_resume_fails_loudly(self) -> None:
        with (
            tempfile.TemporaryDirectory() as directory,
            self.assertRaisesRegex(ValueError, "resume_path"),
        ):
            renderer.load_profile(renderer.MANIFEST, Path(directory))


class RenderingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = renderer.load_profile()
        self.readme = renderer.README.read_text(encoding="utf-8")

    def test_generated_output_is_idempotent(self) -> None:
        once = renderer.render_all(self.profile, self.readme)
        twice = renderer.render_all(self.profile, once[renderer.README])
        self.assertEqual(once, twice)

    def test_only_marked_regions_are_replaced(self) -> None:
        source = (
            "Human prose.\n"
            "<!-- profile:begin:roadmap -->old<!-- profile:end:roadmap -->\n"
        )
        updated, seen = renderer.apply_blocks(source, {"roadmap": "new"})
        self.assertIn("Human prose.", updated)
        self.assertIn("new", updated)
        self.assertNotIn("old", updated)
        self.assertEqual(seen, {"roadmap"})

    def test_missing_duplicate_and_unknown_markers_fail(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing marker"):
            renderer.apply_blocks("plain", {"roadmap": "new"})
        duplicate = (
            "<!-- profile:begin:roadmap --><!-- profile:end:roadmap -->"
            "<!-- profile:begin:roadmap --><!-- profile:end:roadmap -->"
        )
        with self.assertRaisesRegex(ValueError, "duplicate marker"):
            renderer.apply_blocks(duplicate, {"roadmap": "new"})
        unknown = "<!-- profile:begin:other --><!-- profile:end:other -->"
        with self.assertRaisesRegex(ValueError, "unknown marker"):
            renderer.apply_blocks(unknown, {"roadmap": "new"})

    def test_svg_assets_are_static_self_contained_and_accessible(self) -> None:
        for svg in (
            renderer.render_hero(self.profile),
            renderer.render_hero_narrow(self.profile),
            renderer.render_field(self.profile),
            renderer.render_field_narrow(self.profile),
        ):
            renderer.validate_svg(svg)
            root = ET.fromstring(svg)
            self.assertIn("viewBox", root.attrib)
            self.assertIsNotNone(root.find("{http://www.w3.org/2000/svg}title"))
            self.assertIsNotNone(root.find("{http://www.w3.org/2000/svg}desc"))
            lowered = svg.lower()
            for forbidden in (
                "<script",
                "<animate",
                "<image",
                "javascript:",
                "marker-end",
            ):
                self.assertNotIn(forbidden, lowered)

    def test_capability_field_does_not_claim_dependencies_or_maturity(self) -> None:
        fields = (
            renderer.render_field(self.profile),
            renderer.render_field_narrow(self.profile),
        )
        for field in fields:
            lowered = field.lower()
            self.assertIn("independent experiments", lowered)
            self.assertNotIn("status", lowered)
            self.assertNotIn("marker-end", lowered)


class ReadmeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.readme = renderer.README.read_text(encoding="utf-8")

    def test_generated_files_are_current(self) -> None:
        profile = renderer.load_profile()
        wanted = renderer.render_all(profile, self.readme)
        for path, content in wanted.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(path.read_text(encoding="utf-8"), content, path)

    def test_human_readable_word_count_is_compact(self) -> None:
        count = len(visible_words(self.readme))
        self.assertGreaterEqual(count, 150)
        self.assertLessEqual(count, 225)

    def test_black_hole_capture_is_compact_animated_and_motion_safe(self) -> None:
        gif = (ROOT / "assets" / "black-hole.gif").read_bytes()
        still = (ROOT / "assets" / "black-hole-still.png").read_bytes()
        self.assertIn(gif[:6], (b"GIF87a", b"GIF89a"))
        self.assertEqual(struct.unpack("<HH", gif[6:10]), (256, 256))
        self.assertGreaterEqual(gif.count(b"\x21\xf9\x04"), 40)
        self.assertLess(len(gif), 1024 * 1024)
        self.assertEqual(still[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", still[16:24]), (256, 256))
        reduced = 'media="(prefers-reduced-motion: reduce)"'
        self.assertLess(self.readme.index(reduced), self.readme.index("black-hole.gif"))

    def test_sections_do_not_repeat_the_pinned_projects(self) -> None:
        headings = re.findall(r"^## (.+)$", self.readme, flags=re.MULTILINE)
        self.assertEqual(headings, ["Project field", "Next", "Links"])
        for repository in (
            "blackcell",
            "Kernform",
            "cognitive-miniworld",
            "gordian",
            "FabricO11y",
        ):
            self.assertNotIn(f"github.com/kmosoti/{repository}", self.readme)

    def test_learning_os_appears_only_in_later(self) -> None:
        occurrences = [
            line for line in self.readme.splitlines() if "learning-os" in line
        ]
        self.assertEqual(len(occurrences), 1)
        self.assertTrue(occurrences[0].startswith("- **Later:**"))

    def test_retired_profile_material_does_not_return(self) -> None:
        lowered = self.readme.lower()
        for forbidden in ("3,000", "3000", "splunk roles", "skill badge", "trophy"):
            self.assertNotIn(forbidden, lowered)


if __name__ == "__main__":
    unittest.main()
