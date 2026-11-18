# Profile README Contract

The profile README is a compact public workbench, not a résumé or project-status dashboard.

## Authority

`profile.toml` owns identity text, selected project names, URLs, summaries, and links. The renderer owns the profile hero SVGs and the marked README regions. Prose outside the markers remains human-authored.

Run the renderer after changing the manifest:

```bash
python3 tools/render_profile.py
```

Use `--check` in validation. It must never write files in that mode.

## Structure

Keep these sections in order:

1. Name and generated console hero.
2. Three short opening paragraphs covering the workbench, development ecosystem, curiosity, and principled engineering.
3. A generated list of selected public projects.
4. A generated links list.

## Content Rules

- Keep the rendered, human-readable README between 150 and 200 words.
- Give each selected project a direct link and one sentence about what it does.
- Keep paused work and private repositories off the project list.
- Link to the website, `ui-servo`, the résumé, and email.
- Keep work history, operational metrics, generic skill lists, provider criticism, and unverified impact claims out of the README.
- Let each repository own its detailed and changing status.

## Visual Rules

- Use the ember-console palette recorded in the renderer.
- Keep SVGs static and legible against both GitHub themes. Use the narrow hero asset below 600 pixels.
- Include a title and description in each SVG variant and alternative text in the README.
- Do not use scripts, animation elements, external resources, or embedded HTML in SVGs.

## Checks

Run:

```bash
python3 tools/render_profile.py --check
python3 -m unittest discover -s tests -v
vale README.md PROFILE_README_SPEC.md DEPLOY.md
```

Vale must report no errors, warnings, or suggestions before publication.
