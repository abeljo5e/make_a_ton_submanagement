# Contributing

## Before starting
1. Read `README.md`, `docs/TEAM_RESPONSIBILITIES.md`, `docs/API_CONTRACTS.md` and `docs/GIT_WORKFLOW.md`.
2. Confirm your assigned task and files with the team.
3. Pull the latest `main` before creating or updating your feature branch.
4. Never edit another member's owned module without coordinating first.

## Working rules
- One feature branch per member or clearly scoped task.
- Keep pull requests small and focused.
- Do not commit generated folders (`node_modules`, virtual environments, build output).
- Never commit `.env`, secrets, credentials or production data.
- Do not change shared API schemas, database conventions or dependencies without informing the team.
- Add or update tests for changed behavior.
- Update relevant docs when endpoints, schema or setup changes.

## Commit message format
Use:
- `feat: add product variant management`
- `fix: prevent duplicate invoice generation`
- `docs: update API contracts`
- `test: cover monthly billing dates`
- `refactor: extract pricing service`
- `chore: configure Docker development stack`

## Pull request
Every PR must explain:
- What changed and why.
- Which issue/task it addresses.
- How it was tested.
- Screenshots for UI changes.
- API/schema changes and migration instructions.
- Any known limitations.

At least one teammate should review a PR before it is merged. The author should resolve review comments and confirm CI/tests pass.
