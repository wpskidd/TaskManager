

\# Project Development Instructions



You are working in a Git-controlled Python project.



\## Before making changes

\- Check `git status` and identify the active branch.

\- Review relevant source files before editing.

\- Explain your proposed changes.

\- Do not modify files outside the project directory.

\- Never discard uncommitted user changes.



\## During development

\- Make focused, incremental changes.

\- Use Python's standard library unless otherwise approved.

\- Preserve existing functionality.

\- Add or update unit tests for behavioral changes.

\- Never commit secrets, API keys, or environment files.



\## Validation

\- Run `python -m unittest discover -s tests -p "test\*.py" -v`.

\- Diagnose and fix test failures.

\- Review `git diff` before declaring completion.

\- Report all changed files and test results.



\## Git safety

\- Do not push to a remote repository without approval.

\- Do not create commits without explicit authorization.

\- Do not run destructive Git commands such as

&#x20; `git reset --hard`, `git clean -fd`, or forced pushes.

\- Do not merge branches without approval.

\- Ask before deleting files or rewriting history.



