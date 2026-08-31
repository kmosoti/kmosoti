# Profile README Contract

The profile README is a compact public workbench, not a résumé or project-status dashboard.

## Authority

`profile.toml` owns identity text, project capabilities, roadmap text, and links. The renderer owns the profile SVGs and the marked README regions. Prose outside the markers remains human-authored.

Run the renderer after changing the manifest:

```bash
python3 tools/render_profile.py
```

Use `--check` in validation. It must never write files in that mode.

## Structure

Keep these sections in order:

1. Name and generated console hero.
2. Three short opening paragraphs covering the workbench, development ecosystem, curiosity, and principled engineering.
3. A generated capability field that does not imply dependencies or maturity.
4. A generated `Next` roadmap.
5. One collapsed explanation of how to read the workbench.
6. A generated `Links` list.

## Content Rules

- Keep the rendered, human-readable README between 150 and 200 words.
- List exactly five projects in this order: BlackCell, Kernform, ViabilityGrid / cognitive-miniworld, Gordian, and FabricO11y.
- Show those projects once in the capability field. Let GitHub pins provide repository links, with no semantic meaning assigned to pin order.
- Use exactly three roadmap stages: `Now`, `Next`, and `Later`.
- Mention `learning-os` only in `Later`.
- Link to the website, `ui-servo`, the résumé, and email.
- Keep work history, operational metrics, generic skill lists, provider criticism, and unverified impact claims out of the README.
- Let each repository own its detailed and changing status.

## Visual Rules

- Use the ember-console palette recorded in the renderer.
- Keep SVGs static and legible against both GitHub themes. Use the narrow hero and capability-field assets below 600 pixels.
- Include a title, description, and README alternative text for each visual.
- Do not use scripts, animation elements, external resources, or embedded HTML in SVGs.
- Show projects as independent capabilities around the workbench. Lines may show shared context but must not use arrowheads.

## Checks

Run:

```bash
python3 tools/render_profile.py --check
python3 -m unittest discover -s tests -v
vale README.md PROFILE_README_SPEC.md DEPLOY.md
```

Vale must report no errors, warnings, or suggestions before publication.
