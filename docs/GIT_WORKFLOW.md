# Git and GitHub Workflow — Beginner Friendly

## The mental model
- Repository: the shared project.
- `main`: integrated code that should remain runnable.
- Branch: your isolated line of work.
- Commit: a named local checkpoint.
- Push: upload your branch/commits to GitHub.
- Pull: download and integrate remote changes.
- Pull Request (PR): request to merge your branch into `main`.

## One-time setup
```bash
git --version
git config --global user.name "Your Name"
git config --global user.email "your-github-email@example.com"
```

## Clone the team repository
```bash
git clone https://github.com/TEAM-OWNER/Subscription-Management-System.git
cd Subscription-Management-System
```

## Create your assigned branch
```bash
git switch -c auth       # Member 1
git switch -c products   # Member 2
git switch -c billing    # Member 3
git switch -c dashboard  # Member 4
```
Run only the command for your own branch. If the branch already exists locally, use `git switch branch-name`.

## Daily workflow
Start by checking your state:
```bash
git status
git branch --show-current
```

Get latest integrated changes:
```bash
git switch main
git pull origin main
git switch YOUR-BRANCH
git merge main
```
Resolve conflicts if any, test, then continue.

Save and upload your work:
```bash
git add path/to/your/changed/files
git commit -m "feat: describe your change"
git push -u origin YOUR-BRANCH
```
For later pushes:
```bash
git add .
git commit -m "fix: describe the fix"
git push
```

## Pull Request
1. Open the repository on GitHub.
2. Choose Compare & pull request for your branch.
3. Base must be `main`; compare must be your feature branch.
4. Explain changes and tests.
5. Request review from a teammate/leader.
6. Fix review comments and wait for approval.
7. Merge only after checks pass and team agrees.

## Useful commands
```bash
git status
git branch
git branch -a
git switch main
git switch YOUR-BRANCH
git fetch origin
git pull
git log --oneline --graph --all
git diff
git diff --staged
git restore path/to/file
```

## Conflict rules
- Do not panic or delete files to make a conflict disappear.
- Run `git status` to see conflicted files.
- Open each conflict and choose the correct combined content.
- Remove conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).
- Run tests.
- `git add` resolved files and complete the merge commit if Git asks.
- Ask the team before resolving conflicts in shared files.

## Never do these as a beginner
- Do not push directly to `main`.
- Do not use `git push --force` on shared branches.
- Do not commit `.env`, credentials or generated folders.
- Do not run `git reset --hard` unless you fully understand what will be lost.
- Do not merge your own PR if the team requires leader approval.
