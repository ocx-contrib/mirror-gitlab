# mirror-gitlab

OCX mirrors for [GitLab](https://gitlab.com/gitlab-org) tooling. One repository,
one spec directory per package.

| Package | Spec | Publishes to | Announced as | Upstream SPDX |
|---|---|---|---|---|
| [GitLab CLI (`glab`)](https://gitlab.com/gitlab-org/cli) | [`cli/mirror.yml`](cli/mirror.yml) | `ghcr.io/ocx-contrib/gitlab/cli` | `ocx.sh/gitlab/cli` | `MIT` |

Each upstream release is discovered, re-bundled, smoke-tested per
`(version, platform)` and only then pushed with cascade tags, after which the
result is announced into the OCX index.

> This repository previously published the same upstream to the flat coordinate
> `ocx.sh/glab`. `gitlab/cli` is the grouped successor: the vendor beats the org
> handle (`gitlab`, not `gitlab-org`) and the package segment is the name the
> project publishes under, not the binary you type — so `gitlab/cli` ships
> `glab`, exactly as `github/cli` ships `gh`.

## Layout

```
mirror-base.yml         repo-wide policy every spec inherits via `extends:`
cli/
├── mirror.yml          the spec — never at the repo root
├── metadata.json       bundle interface
├── CATALOG.md          → ocx package describe
├── logo.svg / logo.png describe assets, 512px PNG
├── scripts/generate.py url_index generator (GitLab Releases API)
└── tests/smoke.star    Starlark smoke test
```

`LICENSE` and `NOTICE.md` are shared at the root. Logos are **not** — each
package carries its own, because a repo-root `logo.*` sits in no workflow's
`paths:` filter, so replacing it would publish nothing until some unrelated
edit happened to fire.

⚠️ `extends:` is a **shallow** merge of top-level keys. A spec that restates
`platforms:` to change one runner drops every `containers:` entry with it, and
nothing reds — the legs simply stop existing, and every `os.features` claim
goes back to being asserted rather than verified. Restate a block in full or
not at all.

## The `url_index` generator

`glab` publishes through **GitLab Releases on gitlab.com**, not GitHub Releases,
so the native `github_release` source cannot crawl it. `cli/scripts/generate.py`
walks the GitLab Releases API via
[`ocx-mirror-sdk`](https://github.com/ocx-sh/ocx-mirror-sdk)'s
`gitlab.list_releases` and emits a `url_index` of the platform archives.

`uv` is the runtime for that PEP 723 script and is pinned in `ocx.toml` as the
**namespaced** `ocx.sh/astral-sh/uv:0`. The legacy flat `ocx.sh/uv:0` is
forbidden — `mirror-uv` is slated for deletion and that coordinate dies with the
`ocx.sh` host, which would leave the generator with no runtime.

Run it locally with the pinned toolchain:

```bash
uv run cli/scripts/generate.py | head
```

## Platforms

`cli` publishes **six** platform entries: both Linux arches, both macOS arches
and both Windows arches. Upstream builds glab as a pure-Go binary, so there is
one Linux build per arch and it is **fully static** — no `PT_INTERP`, no
`DT_NEEDED`, and no musl/glibc variants to choose between (the `.apk`/`.deb`/
`.rpm` artifacts are the same static binary in three distro wrappers).
`os.features` states what an artifact requires *of the host*, so both Linux keys
are **bare**: tagging them `+libc.musl` would be a false requirement that hid
them from every glibc host. The `alpine:3.20` container leg in `mirror-base.yml`
is what turns that claim into evidence; the measurement itself is recorded above
the `assets:` block in `cli/mirror.yml`.

The version floor is **1.103.0** because `glab_<ver>_windows_arm64.zip` first
ships in v1.103.0 — below it the spec would resolve five platforms and silently
skip the sixth.

## The binaries claim

Every archive — both tarballs and both zips — unpacks to the same four entries
with no wrapper directory: `CHANGELOG.md`, `LICENSE`, `README.md` and
`bin/glab` (`bin/glab.exe` on Windows). So `strip_components` is `0`,
`cli/metadata.json` points PATH at `${installPath}/bin`, and because that is a
real `${installPath}/<dir>` entry `mirror-base.yml` can set `bin_scan: verify` —
the hand-written `binaries: ["glab"]` claim is checked against what the bundle
actually exposes rather than merely asserted. (A raw-binary mirror, whose only
PATH entry is a bare `${installPath}`, has nothing below it to scan and is
rejected at spec load with exit 65; those must use `bin_scan: off`.)

## Editing

| File | Edit | Regenerate after |
|------|------|------------------|
| `mirror-base.yml`, `cli/mirror.yml` | hand | yes — see below |
| `cli/{metadata.json,CATALOG.md,logo.*}` | hand | — |
| `cli/tests/smoke.star`, `cli/scripts/generate.py` | hand | — |
| `.github/workflows/*.yml` | **generated — never hand-edit** | re-run when a spec changes |

```bash
ocx-mirror package pipeline generate ci --spec cli/mirror.yml
```

**Name every spec.** `--spec` *appends* rather than replaces, so a command
naming a subset silently stops rendering the rest while staying green — and the
drift guard reds on a generated workflow the current spec set no longer
produces.

`verify-generated.yml` exits 65 on drift. If a generated workflow is wrong, the
spec or the renderer template is wrong — fix it there and regenerate.

Run `direnv allow` once to put the pinned toolchain on `PATH`, and invoke
`ocx-mirror` directly — never `ocx run -- ocx-mirror`, which pins
`OCX_BINARY_PIN` to the bootstrap `ocx` and false-reds the nested push.

## Bumping the SDK pin

Edit the `[tool.uv.sources]` block at the top of `cli/scripts/generate.py` to
point at a newer wheel:

```toml
ocx-mirror-sdk = { url = "https://github.com/ocx-sh/ocx-mirror-sdk/releases/download/vX.Y.Z/ocx_mirror_sdk-X.Y.Z-py3-none-any.whl" }
```

## Required secrets

| Secret | Use |
|--------|-----|
| `OCX_ANNOUNCE_TOKEN` | opens the index pull request from the `ocx-contrib/index` fork |
| `OCX_MIRROR_DISCORD_HOOK` | notify-stage Discord webhook URL |

(Inherited from the `ocx-contrib` org with visibility ALL. GHCR pushes use the
run's own `GITHUB_TOKEN` — no registry secret needed.)

## License

Apache-2.0 — see [`LICENSE`](LICENSE). Upstream assets are out of scope; each
package's redistribution license is recorded in [`NOTICE.md`](NOTICE.md).
