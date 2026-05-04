# Runbook: Codex CLI Install (Windows)

## Prerequisites

- Node.js v24+ installed (`node --version`)
- npm v11+ installed (`npm --version`)
- Active ChatGPT Plus / Pro / Business / Edu / Enterprise / **Team** subscription

## Install

```bash
npm install -g @openai/codex
```

## Verify

```bash
codex --version
# Expected: codex-cli 0.128.0 (or later)

which codex
# Expected: a path under AppData/Roaming/npm/ or your nodejs install
```

```powershell
# PowerShell:
Get-Command codex
# Expected: a path under AppData\Roaming\npm\ or your nodejs install
```

## First Login

```bash
codex login
```

A browser opens; sign in with your ChatGPT subscription account (e.g. `imaizumi@lineworks.co.jp`). Wait for "Successfully logged in".

```bash
codex login status
# Expected: Logged in using ChatGPT
```

## Confirm Subscription Path (No API Key Billing)

```bash
echo "OPENAI_API_KEY: ${OPENAI_API_KEY:+SET}${OPENAI_API_KEY:-NOT_SET}"
# Expected: NOT_SET (otherwise image gen will use API billing instead of subscription)

grep '"OPENAI_API_KEY"' ~/.codex/auth.json
# Expected: "OPENAI_API_KEY": null,
```

```powershell
# PowerShell:
if ($env:OPENAI_API_KEY) { "OPENAI_API_KEY: SET" } else { "OPENAI_API_KEY: NOT_SET" }
# Expected: OPENAI_API_KEY: NOT_SET

Get-Content "$env:USERPROFILE\.codex\auth.json" | Select-String '"OPENAI_API_KEY"'
# Expected: "OPENAI_API_KEY": null,
```

## Smoke Test

```bash
codex exec --skip-git-repo-check --ephemeral "Reply with exactly: PING_OK" </dev/null
# Expected: stdout includes "PING_OK"
```

```powershell
# PowerShell:
"" | codex exec --skip-git-repo-check --ephemeral "Reply with exactly: PING_OK"
# Expected: stdout includes "PING_OK"
```

## Image Gen Smoke Test (consumes ~22K tokens)

```bash
codex exec --skip-git-repo-check --ephemeral "Test watercolor sketch of a coffee cup. \$imagegen" </dev/null
ls ~/.codex/generated_images/
# Expected: a session-id subdirectory containing ig_*.png
```

```powershell
# PowerShell:
"" | codex exec --skip-git-repo-check --ephemeral "Test watercolor sketch of a coffee cup. `$imagegen"
Get-ChildItem "$env:USERPROFILE\.codex\generated_images\"
# Expected: a session-id subdirectory containing ig_*.png
```
