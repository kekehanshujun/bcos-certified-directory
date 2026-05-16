# BCOS Certified Directory MVP

Static discovery layer for BCOS-certified projects. The directory is built from `data/projects.json` into `dist/index.html`, so entries can be added through a normal pull request without running a backend.

## Live Demo

After GitHub Pages is enabled for the `dist/` folder:

https://kekehanshujun.github.io/bcos-certified-directory/

## Build

```bash
python tools/build.py
```

The build writes:

```text
dist/index.html
docs/index.html
```

`dist/` is the required bounty build output. `docs/` is a deployment mirror because GitHub Pages branch publishing supports `/docs` but not `/dist`.

## Add A Project

1. Edit `data/projects.json`.
2. Add an entry with `name`, `url`, `github`, `category`, `bcos_tier`, `latest_attested_sha`, `sbom_hash`, and `review_note`.
3. Run `python tools/build.py`.
4. Open `dist/index.html` locally or push and let Pages serve it.

## Data Contract

- `bcos_tier`: one of `L0`, `L1`, `L2`
- `category`: one of `agent-infra`, `video`, `blockchain`, `compute-rentals`, `tooling`
- `latest_attested_sha`: latest reviewed commit or release SHA
- `sbom_hash`: `sha256:<64 hex chars>` for the SBOM artifact or SBOM-equivalent attestation artifact

## Included Features

- Search by name, URL, repo, category, or review note
- Filter by category and BCOS tier
- Per-entry badge embed code
- Plain JSON data source for PR-based updates
- Static output, no backend required
