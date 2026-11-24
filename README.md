# Practical skills for Claude

[![tests](../../actions/workflows/tests.yml/badge.svg)](../../actions/workflows/tests.yml)

Agent Skills for Claude Code and claude.ai. Each skill does one job. Skills that run code have unit tests, and the README for each skill reports measured results and limits.

## Skills

| Skill | What it does | Version |
|---|---|---|
| [video-notes-creator](skills/video-notes-creator) | Turns a YouTube video into visual study notes (a web page) with the speaker's real slides, timestamps, and linked resources. Never downloads the video. | 2.0.0 |
| [response-formats](skills/response-formats) | Gives each reply a fixed structure, selected from the intent of the current message and the context of the chat. | 0.1.0 |
| [flow-notes-html](skills/flow-notes-html) | Builds an interactive HTML study page that explains a technical flow end to end, with one example and many diagrams. | 0.1.0 |
| [open-source-repo-explorer](skills/open-source-repo-explorer) | Helps you learn an open source repository and make a first contribution. Gives one HTML page with project health, an architecture map, a traced flow, live issue status and a contribution plan. | 0.2.0 |

## Install

**All skills, from the marketplace (Claude Code):**

```
claude plugin marketplace add ashishkkumar-dev/claude-skills
claude plugin install video-notes-creator@atease
```

In a Claude Code session, `/plugin marketplace add ashishkkumar-dev/claude-skills` does the same.

**One skill, by hand:** copy its folder from `skills/` to `~/.claude/skills/` (all projects) or to `.claude/skills/` in one project.

**claude.ai:** zip one skill folder and upload it as a skill. Code execution must be on.

## Repository layout

```
.claude-plugin/marketplace.json   one entry per skill
skills/<name>/                     one self-contained skill
  SKILL.md                         instructions for Claude
  README.md                        problem, approach, results, limits
  CHANGELOG.md                     versions of this skill
  .claude-plugin/plugin.json       name and version of this skill
  scripts/  tests/  requirements.txt
template/                          copy this to start a new skill
tools/check_skills.py              checks that the repository is consistent
```

Each skill folder works on its own. Skills do not share code.

## Add a skill

1. Copy `template/` to `skills/<name>/`. Use a short kebab-case name.
2. Set the name in `SKILL.md` and `.claude-plugin/plugin.json`. It must match the folder name.
3. Add an entry to `.claude-plugin/marketplace.json` with `"source": "./skills/<name>"`.
4. Add a row to the table above.
5. Run `python tools/check_skills.py` and `python -m pytest skills/<name>/tests`.
6. Tag the release as `<name>-v<version>`, for example `video-notes-creator-v1.0.0`.

CI runs the repository check, then the tests of each skill on Python 3.10 and 3.12.

## Privacy and content

- Personal settings, such as `reader-profile.md`, are in `.gitignore`.
- The repository contains only images that the skills generated. It does not contain other people's slides or full notes made from their videos.

## License

MIT. See [LICENSE](LICENSE).
