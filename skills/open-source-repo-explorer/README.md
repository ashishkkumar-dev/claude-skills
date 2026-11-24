# open-source-repo-explorer

Helps you learn one open source repository and make a first contribution that the maintainers accept. It is for experienced engineers who are new to a codebase, and possibly new to its language. The output is one HTML page.

## The problem

A first contribution to an unknown project needs many separate steps:

- Find out what the project does and where its core is.
- Build it and run its tests.
- Find an issue that nobody else works on.
- Learn the rules for commits, sign-off and PR/MR templates.

Issue status is the hardest step. An issue can look open but have a claim in a comment, or a linked draft PR. Without a check, you can work on an issue that another person already works on.

## How it works

The skill acts as a mentor. It clones the repository, reads the real code, and reads live data from the issue tracker with `gh` or `glab`. Then it builds one HTML page with 11 sections:

| # | Section | What it gives |
|---|---|---|
| 0 | TL;DR | What the project is, the stack, and how good it is for new contributors |
| 1 | Project health | Commits, active maintainers, review and merge time, releases, CI, and a verdict |
| 2 | Architecture map | Mermaid flowchart, directory table with owners, entry points |
| 3 | Trace one flow | Mermaid sequence diagram and a file:line table for each step |
| 4 | Module deep dives | Purpose, types, code walk, tests and gotchas for each core module |
| 5 | Development setup | Exact commands to build, run, test, lint and format |
| 6 | Contribution rules | CONTRIBUTING, CLA/DCO, commit format, templates, channels |
| 7 | Open issues and progress | Live status of each candidate issue, with its assignee, linked PRs/MRs and claims |
| 8 | Recommended issues | The top 3 issues, with files to change, tests and risks |
| 9 | Contribution plan | Steps to merge, a draft issue comment and a draft PR/MR description |
| 10 | Next step | 3 to 5 options to go deeper |

Columns: # = section number in the page; Section = section name; What it gives = the content of the section.

Each claim has an evidence tag, for example [Repo: path:line] or [Issue #N]. In the page, each tag is a link. The skill writes "Not verified" when it cannot check a fact.

## Measured results

Not measured yet.

## Install

```
claude plugin marketplace add ashishkkumar-dev/claude-skills
claude plugin install open-source-repo-explorer@atease
```

Or copy this folder to `~/.claude/skills/`. On claude.ai, zip this folder and upload it as a skill.

## Use

```
/open-source-repo-explorer <repository URL> [area of interest] [hours per week] [target issue]
```

Before you use it, edit the "Reader" section of `SKILL.md` to describe your own background.

## Tests

This skill has no scripts, so it has no unit tests. `python tools/check_skills.py` checks its files.

## Limits

- It needs network access and the `gh` or `glab` CLI for live issue data. Without them, it says what is missing and does not guess the issue status.
- For a large repository, it does sections 0, 1, 2, 7 and 8 first, and asks which section to do next.
- Issue status is correct only at the "Data as of" time in the page.
- It never posts comments, opens issues or PRs/MRs, or pushes code without your approval for each action.
