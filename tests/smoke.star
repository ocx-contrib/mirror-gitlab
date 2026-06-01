# tests/smoke.star — stable across upstream glab releases.
# Asserts machine-stable signals only (exit codes, version digits,
# subcommand presence), never help/banner prose.
GLAB = "glab.exe" if ocx.target_platform.os == ocx.os.Windows else "glab"

# Tier 1 — liveness: the binary resolves on the composed PATH and runs.
r = ocx.run(GLAB, "--version")
expect.ok(r)

# Tier 2 — version shape: digits are the contract, not the banner text.
expect.matches(r.stdout, r"\d+\.\d+\.\d+")

# Tier 3 — subcommand presence: `help <sub>` exits 0 only if the surface
# exists. Proves glab's core command groups without scraping description
# prose, and stays hermetic (no network / no GitLab auth).
expect.eq(ocx.run(GLAB, "help", "mr").exit_code, 0)
expect.eq(ocx.run(GLAB, "help", "issue").exit_code, 0)

# metadata.json declares only PATH (already proven by Tier 1), so there is
# no Tier 4 env-var wiring to assert.
