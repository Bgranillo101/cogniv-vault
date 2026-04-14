# Contributing

## Commit messages

This project uses [Conventional Commits](https://www.conventionalcommits.org/).

```
<type>(<scope>): <short summary>
```

**Types:** `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `ci`, `build`.

**Examples:**

```
feat(agents): add Auditor retry when score < 0.8
fix(ws): guard against reconnect race
docs(adr): record MiniLM embedding decision
```

## Workflow

1. Branch from `main`: `git checkout -b feat/<slug>`
2. Keep commits focused; rebase before PR
3. Ensure CI is green before requesting review
4. Squash-merge on approval

## Local checks

- Backend: `cd backend && uv run ruff check && uv run mypy && uv run pytest`
- Frontend: `pnpm -r lint && pnpm -r typecheck && pnpm -r build`
