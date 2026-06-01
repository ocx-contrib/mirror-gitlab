# /// script
# requires-python = ">=3.13"
# dependencies = ["ocx-mirror-sdk"]
#
# [tool.uv.sources]
# ocx-mirror-sdk = { url = "https://github.com/ocx-sh/ocx-mirror-sdk/releases/download/v0.4.0/ocx_mirror_sdk-0.4.0-py3-none-any.whl" }
# ///
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 The OCX Authors

"""Generate url_index JSON for GitLab CLI (glab) releases.

`glab` publishes its release assets through GitLab Releases on gitlab.com,
not GitHub Releases — so the native `github_release` mirror source cannot
crawl it. `gitlab.list_releases` walks the GitLab Releases API and returns
source-agnostic `Release` objects; we reshape the curated asset links into
a `url_index` document mapping each version to the platform tarballs we
mirror.

Asset names follow `glab_<version>_<os>_<arch>.tar.gz`. We select the Linux
and macOS tarballs only; `mirror.yml`'s `assets:` regex maps those filenames
back to platforms. The SDK surfaces each curated link's stable
`/-/releases/<tag>/downloads/<name>` URL via `browser_download_url`.
"""

import re

from ocx_mirror_sdk import IndexBuilder, gitlab

PROJECT = "gitlab-org/cli"
TAG_RE = re.compile(r"^v(?P<version>\d+\.\d+\.\d+)$")

# Asset-name suffixes for the platforms this mirror ships. Releases that
# predate the lowercase `linux_amd64` naming (≤ v1.45, which used
# `Linux_x86_64`) yield no matching assets and are skipped automatically
# (`add_version` is a no-op when `assets` is empty).
WANTED_SUFFIXES = (
    "_linux_amd64.tar.gz",
    "_linux_arm64.tar.gz",
    "_darwin_amd64.tar.gz",
    "_darwin_arm64.tar.gz",
)


def main() -> None:
    index = IndexBuilder()
    for rel in gitlab.list_releases(PROJECT, include_prereleases=False):
        m = TAG_RE.match(rel.tag_name)
        if not m:
            continue
        assets = {
            a.name: a.browser_download_url
            for a in rel.assets
            if a.name.endswith(WANTED_SUFFIXES)
        }
        if assets:
            index.add_version(m.group("version"), assets=assets, prerelease=rel.prerelease)
    index.emit()


if __name__ == "__main__":
    main()
