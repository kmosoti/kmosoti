# Profile README Contract

The profile README is a compact public workbench, not a résumé or project-status dashboard.

## Structure

Keep these sections in order:

1. Name and professional role.
2. Three short opening paragraphs covering the workbench, development ecosystem, curiosity, and principled engineering.
3. A `Projects` role table.
4. A `Next` roadmap.
5. A `Links` list.

## Content Rules

- Keep the README between 200 and 275 words without padding.
- List exactly five projects in this order: BlackCell, Kernform, ViabilityGrid / cognitive-miniworld, Gordian, and FabricO11y.
- Give each project one role statement and no maturity column.
- Use exactly three roadmap stages: `Now`, `Next`, and `Later`.
- Mention `learning-os` only in `Later`.
- Link to the website, `ui-servo`, the résumé, and email.
- Keep work history, operational metrics, generic skill lists, provider criticism, and unverified impact claims out of the README.
- Let each repository own its detailed and changing status.

## Prose Checks

Run:

```bash
vale README.md PROFILE_README_SPEC.md DEPLOY.md
```

Vale must report no errors, warnings, or suggestions before publication.
