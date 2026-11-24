# Changelog: open-source-repo-explorer

## 0.2.0

- The output is one self-contained HTML page, published as an artifact. A PDF is made only when the reader asks for one.
- Page rules: header with the commit SHA and "Data as of", sticky table of contents, one section for each output section, colored badges for the health verdict and the issue status, light and dark mode, phone width.
- Mermaid diagrams render in the page (Mermaid 10.9.1).
- Evidence tags are links: file lines at the commit SHA, issues, PRs/MRs and docs.
- Drafts in section 9 have a "Copy" button.
- Checks before publish: no console errors, all diagrams render, links work, phone width and dark mode.
- Partial runs mark the missing sections "Not done yet". Later sections go into the same page.

## 0.1.0

First version (on claude.ai only, not in this repository).

- Mentor role for a senior backend engineer who is new to the codebase.
- 11 output sections: TL;DR, project health, architecture map, one traced flow, module deep dives, development setup, contribution rules, open issues and progress, recommended issues, contribution plan, next step.
- Issue status values: Available, Claimed active, Claimed stale, In review, Blocked, Needs triage.
- Evidence tags on each claim. "Not verified" when a fact cannot be checked.
- No comment, issue, PR/MR or push without approval for each action.
- ASD-STE100 writing rules.
