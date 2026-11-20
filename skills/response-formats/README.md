# response-formats

Gives each Claude reply a fixed structure. The structure comes from the intent of the current message, plus context rules from the chat. It is for people who use Claude for long work sessions and want short, predictable answers.

## The problem

In one chat, the intent changes from message to message. For example: learn a concept, then build a page, then ask about a term, then change a diagram. Without fixed rules, replies have these problems:

- Long replies that put the answer at the end.
- Terms that the chat never defined.
- Text that repeats earlier replies.
- A page that becomes messy, because each follow-up adds a new block at the top or bottom.

## How it works

**Reply = fixed template (from the intent of this message) + context rules (from this chat)**

1. **Read the context.** Find the current object (page, doc, design), what the chat already covers, and if the message is a follow-up.
2. **Classify the intent.** Ask 8 questions in a fixed order. The first "yes" gives one of 7 families: Answer, Explain, Fix, Investigate, Make, Co-design, Coach. Personal messages get prose.
3. **Apply the template** of that family. Each template starts with the bottom line.

Rules for the current object: revise, do not rebuild; place new content where it belongs, do not append it; keep the object current.

## Sources for the templates

| Template | Based on |
|---|---|
| All | BLUF (bottom line up front), US Army Regulation 25-50 |
| All | ASD-STE100 Simplified Technical English |
| Explain, Fix | Diátaxis documentation framework (Daniele Procida) |
| Investigate | ICD 203 analytic standards (confidence levels, assumptions kept apart from facts) |
| Co-design | Architecture Decision Records (Michael Nygard) |
| Coach | Situation-Behavior-Impact feedback model (Center for Creative Leadership) |

## Results so far

One manual review only. This is not a measured test.

| Check | Result |
|---|---|
| A 751-line HTML page built over one long chat, scored against the skill rules | 9/16 |
| Causes of the mess in that page that the skill rules prevent | 6 of 8 in version 0.1.0. The 2 missing rules ("place, do not append" and "keep the object current") are added in this version. |

Not measured yet: reply length before and after, and how often Claude selects the correct family.

## Install

```
claude plugin marketplace add ashishkkumar-dev/claude-skills
claude plugin install response-formats@atease
```

Or copy this folder to `~/.claude/skills/`. On claude.ai, zip this folder and upload it as a skill.

## Use

The skill applies to every reply. You do not call it. To make it apply in every chat, add this line to your global instructions: "Use my response-formats skill to select the structure of each reply."

## Tests

This skill has no scripts, so it has no unit tests. `python tools/check_skills.py` checks its files.

## Limits

- Claude classifies the intent. A wrong class gives the wrong template.
- The terms rule can make replies longer when a topic has many new terms.
- The templates are a first version. They will change with use.
