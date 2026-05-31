# /// script
# requires-python = ">=3.13"
# dependencies = ["ocx-mirror-sdk"]
#
# [tool.uv.sources]
# ocx-mirror-sdk = { url = "https://github.com/ocx-sh/ocx-mirror-sdk/releases/download/v0.3.0/ocx_mirror_sdk-0.3.0-py3-none-any.whl" }
# ///
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 The OCX Authors

"""Generate url_index JSON for GitLab CLI (glab) releases.

`glab` publishes its release assets through the GitLab generic package
registry, not GitHub Releases — so `ocx-mirror` cannot crawl it directly.
This script walks the GitLab Releases API and emits a `url_index` document
mapping each version to the platform tarballs we mirror.

Asset names follow `glab_<version>_<os>_<arch>.<ext>`. We select only the
Linux tarballs (`*_linux_amd64.tar.gz`, `*_linux_arm64.tar.gz`); the
`mirror.yml` `assets:` regex maps those filenames back to platforms. Each
asset's `direct_asset_url` is the stable `/-/releases/<tag>/downloads/<name>`
URL, which is what we hand to the downloader.
"""

from ocx_mirror_sdk import IndexBuilder
from ocx_mirror_sdk.http import fetch_json

# URL-encoded path of gitlab-org/cli.
PROJECT = "gitlab-org%2Fcli"
RELEASES_URL = f"https://gitlab.com/api/v4/projects/{PROJECT}/releases"

# Asset-name suffixes for the platforms this mirror ships. `str.endswith`
# accepts a tuple, so this doubles as the platform allow-list.
WANTED_SUFFIXES = (
    "_linux_amd64.tar.gz",
    "_linux_arm64.tar.gz",
)

# Guard against an unbounded crawl if the API ever misbehaves. 100 releases
# per page × 5 pages comfortably covers the whole release history.
MAX_PAGES = 5
PER_PAGE = 100


def main() -> None:
    index = IndexBuilder()

    for page in range(1, MAX_PAGES + 1):
        releases = fetch_json(f"{RELEASES_URL}?per_page={PER_PAGE}&page={page}")
        if not releases:
            break

        for release in releases:
            version = release["tag_name"].lstrip("v")
            assets: dict[str, str] = {}
            for link in release.get("assets", {}).get("links", []):
                name = link["name"]
                if name.endswith(WANTED_SUFFIXES):
                    assets[name] = link["direct_asset_url"]

            # add_version() is a no-op when assets is empty, so releases that
            # predate the lowercase `linux_amd64` asset naming (≤ v1.45, which
            # used `Linux_x86_64`) are skipped automatically.
            index.add_version(
                version,
                assets=assets,
                prerelease=bool(release.get("upcoming_release")),
            )

    index.emit()


if __name__ == "__main__":
    main()
