GLAB = "glab.exe" if ocx.platform()["os"] == "windows" else "glab"

r_version = ocx.run(GLAB, "--version")
expect.ok(r_version)
expect.eq(r_version.exit_code, 0)
expect.contains(r_version.stdout, "glab")

r_help = ocx.run(GLAB, "--help")
expect.eq(r_help.exit_code, 0)
expect.contains(r_help.stdout, "GitLab")
