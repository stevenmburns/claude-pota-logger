# PR Workflow

Complete pull request workflow: commit, push, create PR, and optionally merge.

## Steps

1. Run `git status` and `git diff` to review all changes
2. Create a new feature branch from main if still on main (ask for branch name if not obvious from changes)
3. Stage relevant changed files (not .env or credentials)
4. Commit with a descriptive conventional commit message
5. Push the branch with `-u` flag
6. Create a PR with `gh pr create` including a summary and test plan
7. Report the PR URL
8. Ask the user if they want to merge now — if yes:
   - Merge with `gh pr merge --merge`
   - Switch to main and pull
   - Delete the local and remote feature branch
