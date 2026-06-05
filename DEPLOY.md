# Deploy This As Both Profile And Webpage

This folder is shaped for the single-repo version.

## Option A: One Repo

Use the special GitHub profile repository:

```text
kmosoti/kmosoti
```

Put these files at the root of that repo.

- `README.md` becomes the GitHub profile README.
- `docs/` becomes the GitHub Pages website.
- `assets/` contains README assets.

In GitHub Pages settings:

```text
Source: Deploy from a branch
Branch: main
Folder: /docs
```

The profile appears at:

```text
https://github.com/kmosoti
```

The webpage appears at:

```text
https://kmosoti.github.io/kmosoti/
```

## Option B: Cleaner Root Website URL

Use two repos:

```text
kmosoti/kmosoti          -> profile README
kmosoti/kmosoti.github.io -> root website
```

Put `README.md` and `assets/` in `kmosoti/kmosoti`.

Put the contents of `docs/` in `kmosoti/kmosoti.github.io`.

The webpage then appears at:

```text
https://kmosoti.github.io/
```

If you use Option B, update the website link in `README.md` from:

```text
https://kmosoti.github.io/kmosoti/
```

to:

```text
https://kmosoti.github.io/
```
