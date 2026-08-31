from __future__ import annotations

import re
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
            "<!-- profile:begin:projects -->old<!-- profile:end:projects -->\n"
        )
        updated, seen = renderer.apply_blocks(source, {"projects": "new"})
        self.assertIn("Human prose.", updated)
        self.assertIn("new", updated)
        self.assertNotIn("old", updated)
        self.assertEqual(seen, {"projects"})

    def test_missing_duplicate_and_unknown_markers_fail(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing marker"):
            renderer.apply_blocks("plain", {"projects": "new"})
        duplicate = (
            "<!-- profile:begin:projects --><!-- profile:end:projects -->"
            "<!-- profile:begin:projects --><!-- profile:end:projects -->"
        )
        with self.assertRaisesRegex(ValueError, "duplicate marker"):
            renderer.apply_blocks(duplicate, {"projects": "new"})
        unknown = "<!-- profile:begin:other --><!-- profile:end:other -->"
        with self.assertRaisesRegex(ValueError, "unknown marker"):
            renderer.apply_blocks(unknown, {"projects": "new"})

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
        self.assertGreaterEqual(count, 200)
        self.assertLessEqual(count, 275)

    def test_sections_and_project_rows_are_exact(self) -> None:
        headings = re.findall(r"^## (.+)$", self.readme, flags=re.MULTILINE)
        self.assertEqual(headings, ["Project field", "Projects", "Next", "Links"])
        rows = re.findall(
            r"^\| \[([^]]+)]\(https://github.com/kmosoti/[^)]+\) \|",
            self.readme,
            re.MULTILINE,
        )
        self.assertEqual(rows, renderer.EXPECTED_PROJECTS)

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
