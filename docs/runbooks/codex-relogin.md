# Runbook: Codex Re-login (when token expires)

## Symptom

Running `codex exec ...` produces:

```
ERROR: Your access token could not be refreshed because your refresh token
was already used. Please log out and sign in again.
```

`codex login status` may **falsely report** "Logged in using ChatGPT" — it only reads the local file, it does not test the token against the server. Trust the runtime error, not the status command.

## Cause

Codex stores OAuth tokens in `~/.codex/auth.json`. Access tokens have ~10-day TTL; refresh tokens are single-use. If the refresh window is missed (e.g. machine offline for weeks), both are dead.

## Recovery

```bash
codex logout
# Expected: Successfully logged out

codex login
# Browser opens — sign in with your ChatGPT account
# Expected: Successfully logged in
```

## Verify

```bash
codex exec --skip-git-repo-check --ephemeral "Reply with: OK" </dev/null
# Expected: stdout includes "OK"
```

## Prevention

- Run `/new-4koma` (or any `codex exec`) at least every ~10 days to keep the refresh token fresh.
- The `4koma-image-gen` skill includes a pre-flight check that runs `codex exec ... "ping"` and exits early with this runbook link if the call fails 401.
