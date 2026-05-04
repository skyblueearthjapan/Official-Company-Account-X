# Runbook: Weekly 4-koma Generation Flow

This is the standard operating procedure for producing one weekly episode.

## Trigger

Manual. The 今泉課長 decides when to run it. There is no scheduled automation in Phase 1.

## Step 1: Open Claude Code in the workspace

Either:
- **CLI**: `cd "C:/Users/imaizumi.LINEWORKS-NET/Documents/会社公式アカウントＸ運用" && claude`
- **Desktop**: open Claude Code Desktop app, point to the project folder

## Step 2: Pre-flight (recommended ~once per week)

```bash
codex exec --skip-git-repo-check --ephemeral "Reply: OK" </dev/null
```

If this fails with `401` or "refresh token", follow [`codex-relogin.md`](codex-relogin.md).

## Step 3: Trigger generation

In Claude Code, type:

```
/new-4koma "<お題>"
```

Example:

```
/new-4koma "今週は新工場の社員食堂でセバスチャンが配膳ロボとぶつかる話"
```

Optional `--patterns N` to control parallel pattern count (default 4):

```
/new-4koma "..." --patterns 3
```

## Step 4: Wait for generation

The agent creates `episodes/<連番>-<日付>-<タイトル>/` and produces 4 patterns in parallel. Each pattern includes:

- `pattern-{a,b,c,d}/plot.md` — plot + dialogue
- `pattern-{a,b,c,d}/prompt.md` — final prompt sent to Codex
- `pattern-{a,b,c,d}/generated.png` — the 4-koma image

Total time: ~3-5 minutes (parallel). Total quota: ~90K tokens.

## Step 5: Review

Open the four `generated.png` files side-by-side. Decide:

- **Adopt one as-is** → `/finalize-4koma <ep-id> <pattern>`
- **Refine one** → `/refine-4koma <ep-id> <pattern> "<指示>"`
- **Mix two** → manually edit `final/plot.md`, then `/refine-4koma <ep-id> final "<指示>"`

## Step 6: Finalize

```
/finalize-4koma <ep-id> <pattern>
```

This copies the chosen pattern's `plot.md`, `prompt.md`, and `generated.png` to `episodes/<id>/final/` and prompts you to fill in `notes.md` with the rationale.

## Step 7 (Phase 3 only): Ship

```
/ship-4koma <ep-id>
```

Will be implemented when X API is wired in Phase 3. **Phase 1 stops at finalize.**

## Troubleshooting

| Symptom | Action |
|---------|--------|
| `codex` 401 error | [codex-relogin.md](codex-relogin.md) |
| All 4 patterns look identical | Re-run with a more specific お題 |
| Character looks wrong | Check `characters/<id>/reference/` images exist; refine character `anchor.md` |
| Style drifted | Verify the requested preset name matches `style-guide/<preset>/` |
