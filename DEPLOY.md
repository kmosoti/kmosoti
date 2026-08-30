# Profile and Website Surfaces

The public presence has three distinct parts.

| Surface | Purpose | Authority |
| --- | --- | --- |
| `kmosoti/kmosoti` | GitHub profile README and profile-owned assets | Authoritative for the GitHub profile only |
| `kmosoti/ui-servo` | Website source, build logic, direction contract, and quality gates | Authoritative for website implementation |
| `kennedy.mosoti.dev` | Published personal website | Authoritative public website |

The old `kmosoti.github.io` deployment is not an authoritative source or portfolio. If retained, it should contain only a minimal redirect to `kennedy.mosoti.dev` so old links continue to resolve.

## Profile Repository Responsibilities

- Maintain a concise GitHub-native introduction.
- Point to the authoritative website and current projects.
- Store the résumé linked from the profile.
- Describe paused work honestly.
- Pass the repository's prose checks.

## Website Responsibilities

All website design and implementation changes begin in `ui-servo`. Its export process produces the deployable site only after deterministic checks and visual review complete.

Do not edit generated website output as a substitute for changing `ui-servo`.

## Prose Checks

Install Vale, then run:

```bash
vale sync
vale README.md DEPLOY.md
```

The repository keeps the Vale configuration under version control and ignores downloaded style packages.
