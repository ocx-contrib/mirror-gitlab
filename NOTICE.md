# NOTICE

This repository packages and redistributes upstream software published by
[GitLab](https://gitlab.com/gitlab-org). The Apache-2.0 license in
[`LICENSE`](LICENSE) covers the OCX pipeline files authored here. It does
**not** cover any upstream-derived asset — each package's redistributed bytes
carry their own license, recorded below.

Each package's logo is reproduced for catalog identification only, under
nominative fair use. The marks remain the property of their respective owners
and no endorsement is implied.

| Package | GHCR path | Upstream SPDX |
|---|---|---|
| `cli` | `ghcr.io/ocx-contrib/gitlab/cli` | `MIT` |

---

## `cli`

Upstream: <https://gitlab.com/gitlab-org/cli>
Published to `ghcr.io/ocx-contrib/gitlab/cli`.

| Component | SPDX | Holder |
|---|---|---|
| GitLab CLI (`glab`) | **MIT** | GitLab Inc. (2022–present); GitHub Inc. (2019) |

The SPDX id is read off the `LICENSE` file upstream ships inside every release
archive (`MIT License / Copyright (c) 2022-present GitLab Inc. / Copyright (c)
2019 GitHub Inc.`) — `gitlab-org/cli` is hosted on gitlab.com, so there is no
GitHub licence endpoint to query. MIT is permissive and grants redistribution
outright; no Corresponding Source duty attaches.

The GitLab logo shipped with this package is a GitLab B.V. trademark.

No modifications are made to the upstream artifacts; they are republished
byte-for-byte inside an OCX bundle.
