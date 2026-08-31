#!/usr/bin/env python3
"""Render deterministic GitHub profile blocks and SVGs from profile.toml."""

from __future__ import annotations

import argparse
import html
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import tomllib

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "profile.toml"
README = ROOT / "README.md"
HERO = ROOT / "assets" / "profile-hero.svg"
HERO_NARROW = ROOT / "assets" / "profile-hero-narrow.svg"
FIELD = ROOT / "assets" / "project-field.svg"
FIELD_NARROW = ROOT / "assets" / "project-field-narrow.svg"

EXPECTED_PROJECTS = [
    "BlackCell",
    "Kernform",
    "ViabilityGrid / cognitive-miniworld",
    "Gordian",
    "FabricO11y",
]

PALETTE = {
    "background": "#0a0b0d",
    "surface": "#141619",
    "text": "#eae5db",
    "muted": "#8b9096",
    "border": "#262a2f",
    "ember": "#ff7a45",
    "amber": "#f2b134",
}

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

MARKER = re.compile(
    r"(?P<open><!--\s*profile:begin:(?P<name>[\w-]+)\s*-->)"
    r".*?"
    r"(?P<close><!--\s*profile:end:(?P=name)\s*-->)",
    re.DOTALL,
)


@dataclass(frozen=True)
class Project:
    id: str
    name: str
    url: str
    capability: str
    role: str


@dataclass(frozen=True)
class Profile:
    identity: dict[str, str]
    workbench: dict[str, str]
    projects: tuple[Project, ...]
    roadmap: dict[str, str]
    links: dict[str, str]


def _exact_keys(name: str, value: dict[str, object], expected: set[str]) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        details = []
        if missing:
            details.append("missing " + ", ".join(missing))
        if unknown:
            details.append("unknown " + ", ".join(unknown))
        raise ValueError(f"{name}: {'; '.join(details)}")


def _string_table(name: str, value: object, expected: set[str]) -> dict[str, str]:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a table")
    _exact_keys(name, value, expected)
    result: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{name}.{key} must be a non-empty string")
        result[key] = item.strip()
    return result


def _https_url(name: str, value: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"{name} must be an absolute HTTPS URL")


def load_profile(path: Path = MANIFEST, root: Path = ROOT) -> Profile:
    with path.open("rb") as stream:
        raw = tomllib.load(stream)

    _exact_keys(
        "profile.toml",
        raw,
        {"schema_version", "identity", "workbench", "projects", "roadmap", "links"},
    )
    if raw["schema_version"] != 1:
        raise ValueError("schema_version must be 1")

    identity = _string_table("identity", raw["identity"], {"name", "role", "thesis"})
    workbench = _string_table("workbench", raw["workbench"], {"title", "subtitle"})
    roadmap = _string_table(
        "roadmap",
        raw["roadmap"],
        {"now", "next", "later", "paused_name", "paused_url"},
    )
    links = _string_table(
        "links",
        raw["links"],
        {
            "website_label",
            "website_url",
            "source_label",
            "source_url",
            "resume_label",
            "resume_path",
            "email_label",
            "email_address",
        },
    )

    project_rows = raw["projects"]
    if not isinstance(project_rows, list):
        raise TypeError("projects must be an array of tables")
    projects: list[Project] = []
    for index, row in enumerate(project_rows):
        values = _string_table(
            f"projects[{index}]", row, {"id", "name", "url", "capability", "role"}
        )
        _https_url(f"projects[{index}].url", values["url"])
        projects.append(Project(**values))

    names = [project.name for project in projects]
    if names != EXPECTED_PROJECTS:
        raise ValueError("projects must appear in the documented five-project order")
    ids = [project.id for project in projects]
    if len(ids) != len(set(ids)):
        raise ValueError("project ids must be unique")

    for key in ("website_url", "source_url"):
        _https_url(f"links.{key}", links[key])
    _https_url("roadmap.paused_url", roadmap["paused_url"])
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", links["email_address"]):
        raise ValueError("links.email_address is invalid")

    resume = (root / links["resume_path"]).resolve()
    if not resume.is_file() or root.resolve() not in resume.parents:
        raise ValueError(
            "links.resume_path must name a file inside the profile repository"
        )

    return Profile(identity, workbench, tuple(projects), roadmap, links)


def _xml(value: str) -> str:
    return html.escape(value, quote=True)


def _md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_hero(profile: Profile) -> str:
    identity = profile.identity
    p = PALETTE
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 280" role="img" aria-labelledby="title description">
  <title id="title">{_xml(identity["name"])} — {_xml(identity["role"])}</title>
  <desc id="description">{_xml(identity["thesis"])}</desc>
  <rect width="1200" height="280" rx="14" fill="{p["background"]}"/>
  <rect x="1" y="1" width="1198" height="278" rx="13" fill="none" stroke="{p["border"]}" stroke-width="2"/>
  <path d="M1 48H1199" stroke="{p["border"]}"/>
  <circle cx="24" cy="24" r="5" fill="{p["ember"]}"/>
  <circle cx="43" cy="24" r="5" fill="{p["amber"]}" opacity=".7"/>
  <circle cx="62" cy="24" r="5" fill="{p["muted"]}" opacity=".45"/>
  <text x="84" y="29" fill="{p["muted"]}" font-family="{MONO}" font-size="14">kennedy@workbench — profile</text>
  <text x="1138" y="29" text-anchor="end" fill="{p["muted"]}" font-family="{MONO}" font-size="13">public / inspectable</text>
  <text x="48" y="92" fill="{p["ember"]}" font-family="{MONO}" font-size="18">$ whoami</text>
  <text x="48" y="151" fill="{p["text"]}" font-family="{MONO}" font-size="44" font-weight="700">{_xml(identity["name"])}</text>
  <text x="49" y="184" fill="{p["ember"]}" font-family="{MONO}" font-size="17" letter-spacing="1.8">{_xml(identity["role"].upper())}</text>
  <text x="49" y="229" fill="{p["muted"]}" font-family="{MONO}" font-size="18">{_xml(identity["thesis"])}</text>
  <g transform="translate(1038 150)" fill="none" stroke="{p["ember"]}">
    <ellipse rx="100" ry="35" opacity=".2"/>
    <ellipse rx="73" ry="73" opacity=".18" transform="rotate(35)"/>
    <ellipse rx="52" ry="94" opacity=".14" transform="rotate(-55)"/>
    <circle r="27" fill="{p["surface"]}" stroke-width="1.5" opacity=".95"/>
    <circle cx="94" cy="-12" r="4" fill="{p["ember"]}" stroke="none"/>
    <circle cx="-52" cy="-58" r="3" fill="{p["amber"]}" stroke="none"/>
    <circle cx="-35" cy="77" r="3" fill="{p["muted"]}" stroke="none"/>
  </g>
</svg>
'''


def render_hero_narrow(profile: Profile) -> str:
    identity = profile.identity
    p = PALETTE
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 430" role="img" aria-labelledby="title description">
  <title id="title">{_xml(identity["name"])} — {_xml(identity["role"])}</title>
  <desc id="description">{_xml(identity["thesis"])}</desc>
  <rect width="640" height="430" rx="14" fill="{p["background"]}"/>
  <rect x="1" y="1" width="638" height="428" rx="13" fill="none" stroke="{p["border"]}" stroke-width="2"/>
  <path d="M1 48H639" stroke="{p["border"]}"/>
  <circle cx="24" cy="24" r="5" fill="{p["ember"]}"/>
  <circle cx="43" cy="24" r="5" fill="{p["amber"]}" opacity=".7"/>
  <circle cx="62" cy="24" r="5" fill="{p["muted"]}" opacity=".45"/>
  <text x="84" y="29" fill="{p["muted"]}" font-family="{MONO}" font-size="14">kennedy@workbench</text>
  <text x="36" y="91" fill="{p["ember"]}" font-family="{MONO}" font-size="18">$ whoami</text>
  <text x="36" y="148" fill="{p["text"]}" font-family="{MONO}" font-size="40" font-weight="700">{_xml(identity["name"])}</text>
  <text x="37" y="184" fill="{p["ember"]}" font-family="{MONO}" font-size="15" letter-spacing="1.4">{_xml(identity["role"].upper())}</text>
  <text x="37" y="241" fill="{p["muted"]}" font-family="{MONO}" font-size="18">Build the tools.</text>
  <text x="37" y="271" fill="{p["muted"]}" font-family="{MONO}" font-size="18">Test the assumptions.</text>
  <text x="37" y="301" fill="{p["muted"]}" font-family="{MONO}" font-size="18">Make the evidence visible.</text>
  <g transform="translate(520 315)" fill="none" stroke="{p["ember"]}">
    <ellipse rx="76" ry="27" opacity=".2"/>
    <ellipse rx="55" ry="55" opacity=".18" transform="rotate(35)"/>
    <ellipse rx="39" ry="71" opacity=".14" transform="rotate(-55)"/>
    <circle r="21" fill="{p["surface"]}" stroke-width="1.5" opacity=".95"/>
    <circle cx="71" cy="-9" r="4" fill="{p["ember"]}" stroke="none"/>
    <circle cx="-39" cy="-44" r="3" fill="{p["amber"]}" stroke="none"/>
  </g>
  <text x="36" y="394" fill="{p["muted"]}" font-family="{MONO}" font-size="13">public / inspectable</text>
</svg>
'''


def _node(project: Project, x: int, y: int) -> str:
    p = PALETTE
    name_lines = project.name.split(" / ", maxsplit=1)
    if len(name_lines) == 2:
        title = (
            f'<text x="{x + 24}" y="{y + 37}" fill="{p["text"]}" font-family="{MONO}" '
            f'font-size="18" font-weight="700">{_xml(name_lines[0])}</text>'
            f'<text x="{x + 24}" y="{y + 60}" fill="{p["text"]}" font-family="{MONO}" '
            f'font-size="15">/ {_xml(name_lines[1])}</text>'
            f'<text x="{x + 24}" y="{y + 86}" fill="{p["amber"]}" font-family="{MONO}" '
            f'font-size="13" letter-spacing="1">{_xml(project.capability.upper())}</text>'
        )
    else:
        title = (
            f'<text x="{x + 24}" y="{y + 43}" fill="{p["text"]}" font-family="{MONO}" '
            f'font-size="20" font-weight="700">{_xml(project.name)}</text>'
            f'<text x="{x + 24}" y="{y + 75}" fill="{p["amber"]}" font-family="{MONO}" '
            f'font-size="13" letter-spacing="1">{_xml(project.capability.upper())}</text>'
        )
    return (
        f'<g><rect x="{x}" y="{y}" width="320" height="104" rx="8" '
        f'fill="{p["surface"]}" stroke="{p["border"]}"/>{title}</g>'
    )


def render_field(profile: Profile) -> str:
    p = PALETTE
    positions = [(40, 228), (440, 40), (140, 490), (840, 228), (740, 490)]
    nodes = "\n  ".join(
        _node(project, x, y)
        for project, (x, y) in zip(profile.projects, positions, strict=True)
    )
    title = _xml(profile.workbench["title"])
    subtitle = _xml(profile.workbench["subtitle"])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 640" role="img" aria-labelledby="title description">
  <title id="title">Five-project development workbench capability field</title>
  <desc id="description">Five independent projects grouped around a shared development workbench without dependency arrows.</desc>
  <rect width="1200" height="640" rx="14" fill="{p["background"]}"/>
  <rect x="1" y="1" width="1198" height="638" rx="13" fill="none" stroke="{p["border"]}" stroke-width="2"/>
  <g stroke="{p["border"]}" stroke-width="1.5" opacity=".9">
    <line x1="440" y1="302" x2="360" y2="280"/>
    <line x1="600" y1="250" x2="600" y2="144"/>
    <line x1="520" y1="370" x2="376" y2="490"/>
    <line x1="760" y1="302" x2="840" y2="280"/>
    <line x1="680" y1="370" x2="824" y2="490"/>
  </g>
  <g>
    <rect x="440" y="250" width="320" height="120" rx="10" fill="{p["surface"]}" stroke="{p["ember"]}" stroke-width="1.5"/>
    <text x="600" y="303" text-anchor="middle" fill="{p["text"]}" font-family="{MONO}" font-size="22" font-weight="700">{title}</text>
    <text x="600" y="335" text-anchor="middle" fill="{p["ember"]}" font-family="{MONO}" font-size="14" letter-spacing="1.5">{subtitle}</text>
  </g>
  {nodes}
  <text x="34" y="34" fill="{p["muted"]}" font-family="{MONO}" font-size="13">capability field / independent experiments / no maturity claims</text>
</svg>
'''


def render_field_narrow(profile: Profile) -> str:
    p = PALETTE
    center_title = _xml(profile.workbench["title"])
    center_subtitle = _xml(profile.workbench["subtitle"])
    node_y = [230, 390, 550, 710, 870]
    nodes = "\n  ".join(
        _node(project, 60, y)
        for project, y in zip(profile.projects, node_y, strict=True)
    ).replace('width="320"', 'width="520"')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 1020" role="img" aria-labelledby="title description">
  <title id="title">Five-project development workbench capability field</title>
  <desc id="description">Five independent projects listed around a shared development workbench without dependency arrows or ordering.</desc>
  <rect width="640" height="1020" rx="14" fill="{p["background"]}"/>
  <rect x="1" y="1" width="638" height="1018" rx="13" fill="none" stroke="{p["border"]}" stroke-width="2"/>
  <text x="30" y="34" fill="{p["muted"]}" font-family="{MONO}" font-size="13">capability field / independent experiments / no dependency order</text>
  <g>
    <rect x="60" y="65" width="520" height="120" rx="10" fill="{p["surface"]}" stroke="{p["ember"]}" stroke-width="1.5"/>
    <text x="320" y="118" text-anchor="middle" fill="{p["text"]}" font-family="{MONO}" font-size="22" font-weight="700">{center_title}</text>
    <text x="320" y="150" text-anchor="middle" fill="{p["ember"]}" font-family="{MONO}" font-size="14" letter-spacing="1.5">{center_subtitle}</text>
  </g>
  {nodes}
</svg>
'''


def render_blocks(profile: Profile) -> dict[str, str]:
    project_rows = ["| Project | Role |", "| --- | --- |"]
    for project in profile.projects:
        project_rows.append(
            f"| [{_md(project.name)}]({project.url}) | {_md(project.role)} |"
        )

    roadmap = profile.roadmap
    roadmap_rows = [
        f"- **Now:** {_md(roadmap['now'])}",
        f"- **Next:** {_md(roadmap['next'])}",
        (
            f"- **Later:** {_md(roadmap['later'])} "
            f"[{_md(roadmap['paused_name'])}]({roadmap['paused_url']})."
        ),
    ]

    links = profile.links
    link_rows = [
        f"- Website: [{_md(links['website_label'])}]({links['website_url']})",
        f"- Website source and build system: [{_md(links['source_label'])}]({links['source_url']})",
        f"- [{_md(links['resume_label'])}]({links['resume_path']})",
        f"- [{_md(links['email_label'])}](mailto:{links['email_address']})",
    ]
    return {
        "projects": "\n".join(project_rows),
        "roadmap": "\n".join(roadmap_rows),
        "links": "\n".join(link_rows),
    }


def apply_blocks(readme: str, blocks: dict[str, str]) -> tuple[str, set[str]]:
    seen: set[str] = set()

    def replace(match: re.Match[str]) -> str:
        name = match["name"]
        if name in seen:
            raise ValueError(f"duplicate marker pair: {name}")
        seen.add(name)
        if name not in blocks:
            raise ValueError(f"unknown marker pair: {name}")
        return f"{match['open']}\n{blocks[name]}\n{match['close']}"

    updated = MARKER.sub(replace, readme)
    missing = set(blocks) - seen
    if missing:
        raise ValueError(
            "README is missing marker pairs for: " + ", ".join(sorted(missing))
        )
    return updated, seen


def render_all(profile: Profile, readme: str) -> dict[Path, str]:
    updated, _ = apply_blocks(readme, render_blocks(profile))
    return {
        README: updated,
        HERO: render_hero(profile),
        HERO_NARROW: render_hero_narrow(profile),
        FIELD: render_field(profile),
        FIELD_NARROW: render_field_narrow(profile),
    }


def validate_svg(svg: str) -> None:
    root = ET.fromstring(svg)
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("generated asset is not an SVG")
    if "viewBox" not in root.attrib:
        raise ValueError("generated SVG has no viewBox")
    lowered = svg.lower()
    forbidden = ("<script", "<animate", "javascript:", "<foreignobject", "<image")
    if any(token in lowered for token in forbidden):
        raise ValueError("generated SVG contains unsafe or animated content")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="fail if committed output has drifted"
    )
    args = parser.parse_args(argv)

    try:
        profile = load_profile()
        outputs = render_all(profile, README.read_text(encoding="utf-8"))
        validate_svg(outputs[HERO])
        validate_svg(outputs[HERO_NARROW])
        validate_svg(outputs[FIELD])
        validate_svg(outputs[FIELD_NARROW])
    except (
        OSError,
        TypeError,
        ValueError,
        tomllib.TOMLDecodeError,
        ET.ParseError,
    ) as error:
        print(f"profile render failed: {error}", file=sys.stderr)
        return 2

    if args.check:
        stale = [
            str(path.relative_to(ROOT))
            for path, wanted in outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != wanted
        ]
        if stale:
            print(
                "stale generated profile output: " + ", ".join(stale), file=sys.stderr
            )
            return 1
        print("profile README and SVG assets are current")
        return 0

    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
