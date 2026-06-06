# Profile And Website Deployment

This repository is the GitHub profile repository:

```text
kmosoti/kmosoti
```

Its `README.md` renders at:

```text
https://github.com/kmosoti
```

The full website now lives in the separate root Pages repository:

```text
kmosoti/kmosoti.github.io
```

That site renders at:

```text
https://kmosoti.github.io/
```

## Local Repos

Expected local paths:

```text
C:\Users\kenne\Documents\personal_directory\Projects\kmosoti
C:\Users\kenne\Documents\personal_directory\Projects\kmosoti.github.io
```

## Profile Repo Responsibilities

- Short front-door README.
- Resume asset used by the profile.
- Banner image used by the profile.
- No generated notebook pages.

## Website Repo Responsibilities

- Static Systems Notebook website.
- Markdown content source.
- Python renderer.
- Generated root HTML for branch-based Pages.
- GitHub Actions workflow for `_site` artifact deployment.
