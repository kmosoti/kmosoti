# Profile and Website Surfaces

The public presence has three distinct parts.

| Surface | Purpose | Authority |
| --- | --- | --- |
| `kmosoti/kmosoti` | GitHub profile README, manifest, renderer, and profile-owned assets | Authoritative for the GitHub profile |
| `kmosoti/ui-servo` | Website source, build logic, direction contract, and quality gates | Authoritative for website implementation |
| `kennedy.mosoti.dev` | Published personal website | Authoritative public website |

The old `kmosoti.github.io` deployment is not an authoritative source or portfolio. If retained, it should contain only a minimal redirect to `kennedy.mosoti.dev` so old links continue to resolve.

## Profile Publication

Change factual profile data in `profile.toml`, then regenerate and check the committed output:

```bash
python3 tools/render_profile.py
python3 tools/render_profile.py --check
python3 -m unittest discover -s tests -v
vale README.md PROFILE_README_SPEC.md DEPLOY.md
```

The GitHub Actions workflow repeats these checks with read-only repository permissions. It reports drift but never commits generated files.

Publish all profile changes from this repository. Website deployment must not push into the profile repository.

## Website Publication

All website design and implementation changes begin in `ui-servo`. Its export process produces the deployable site only after deterministic checks and visual review complete.

Do not edit generated website output as a substitute for changing `ui-servo`.
