# cli/tests/smoke.star — stable across upstream glab releases.
# Assert on the contract (exit code, version shape, a value glab stored and
# read back), never on help/banner prose — upstream's wording is theirs to
# change, the digits and the round-trip are not.
GLAB = "glab.exe" if ocx.target_platform.os == ocx.os.Windows else "glab"

# glab is a GitLab client, so its default posture is to talk to gitlab.com: it
# POSTs a telemetry event after a mutating command and polls the releases API
# for an update check. Both are best-effort (they warn and still exit 0), but a
# smoke test must not depend on egress, and it must not write into the runner's
# real HOME — so both are turned off by glab's own env knobs and the config dir
# is redirected. GLAB_CONFIG_DIR is the portable redirect: it needs no per-OS
# env name (HOME vs %AppData%), and a relative value resolves against the
# script's cwd, which is the per-run scratch root. Measured on v1.111.0 — with
# this overlay the round-trip below makes zero network calls and writes nothing
# outside scratch.
ENV = {
    "GLAB_CONFIG_DIR": "glab-cfg",
    "GLAB_SEND_TELEMETRY": "false",
    "GLAB_CHECK_UPDATE": "false",
}

# Tier 1 + 2 — liveness and version SHAPE: the binary resolves on the composed
# PATH, runs, and prints digits. `glab --version` touches no network at all.
r = ocx.run(GLAB, "--version", env = ENV)
expect.ok(r)
expect.matches(r.stdout, r"\d+\.\d+\.\d+")

# Tier 3 — offline config round-trip: glab parses the write, persists it to its
# own config file and reads the same value back. This is the check that fails
# if the config layer regresses or the shipped binary is truncated, and it
# proves useful work without a GitLab host or credentials.
#
# `remote_alias` deliberately, not `editor`: glab lets an environment variable
# shadow a config key on read, and EDITOR/VISUAL are commonly set on a
# developer's machine — that round-trip would read back the shell's editor and
# never touch the config file. Nothing sets REMOTE_ALIAS. The value is a token
# chosen here, so an anchored match cannot pass on some upstream default.
s = ocx.run(GLAB, "config", "set", "-g", "remote_alias", "ocx-smoke", env = ENV)
expect.ok(s)
g = ocx.run(GLAB, "config", "get", "-g", "remote_alias", env = ENV)
expect.ok(g)
expect.matches(g.stdout, r"^ocx-smoke\s*$")

# metadata.json declares only PATH (already proven by Tier 1), so there is
# no Tier 4 env-var wiring to assert.
