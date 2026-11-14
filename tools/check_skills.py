#!/usr/bin/env python3
"""Check that the repository is consistent. Exit 1 on the first list of problems.

For each folder in skills/:
- SKILL.md exists, has front matter, its `name` equals the folder name, and it has a `description`.
- .claude-plugin/plugin.json has the same name and a version, and CHANGELOG.md has a section for it.
- README.md and CHANGELOG.md exist.
- The marketplace has an entry with the same name and source "./skills/<name>".
- The root README catalog links to the folder.
Also: each marketplace entry points to an existing skill folder.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def front_matter(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m: return None
    return dict(re.findall(r"^(\w[\w-]*):\s*(.*)$", m.group(1), re.M))


def problems(root=ROOT):
    out = []
    skills_dir = os.path.join(root, "skills")
    skills = sorted(d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d)) and not d.startswith("."))
    market = json.load(open(os.path.join(root, ".claude-plugin", "marketplace.json"), encoding="utf-8"))
    for key in ("name", "owner", "plugins"):
        if key not in market: out.append(f"marketplace.json: missing '{key}'")
    entries = {p.get("name"): p for p in market.get("plugins", [])}
    catalog = open(os.path.join(root, "README.md"), encoding="utf-8").read()
    for s in skills:
        d = os.path.join(skills_dir, s)
        fm = front_matter(os.path.join(d, "SKILL.md")) if os.path.exists(os.path.join(d, "SKILL.md")) else None
        if fm is None: out.append(f"{s}: SKILL.md missing or has no front matter")
        else:
            if fm.get("name", "").strip().strip('"') != s: out.append(f"{s}: SKILL.md name is '{fm.get('name')}', expected '{s}'")
            if not fm.get("description", "").strip(): out.append(f"{s}: SKILL.md has no description")
        pj = os.path.join(d, ".claude-plugin", "plugin.json")
        if not os.path.exists(pj): out.append(f"{s}: .claude-plugin/plugin.json missing")
        else:
            m = json.load(open(pj, encoding="utf-8"))
            if m.get("name") != s: out.append(f"{s}: plugin.json name is '{m.get('name')}', expected '{s}'")
            if not m.get("version"): out.append(f"{s}: plugin.json has no version")
            elif f"## {m['version']}" not in open(os.path.join(d, "CHANGELOG.md"), encoding="utf-8").read() if os.path.exists(os.path.join(d, "CHANGELOG.md")) else False:
                out.append(f"{s}: CHANGELOG.md has no section for version {m['version']}")
        for f in ("README.md", "CHANGELOG.md"):
            if not os.path.exists(os.path.join(d, f)): out.append(f"{s}: {f} missing")
        e = entries.get(s)
        if not e: out.append(f"{s}: no marketplace entry")
        elif e.get("source") != f"./skills/{s}": out.append(f"{s}: marketplace source is '{e.get('source')}', expected './skills/{s}'")
        if f"(skills/{s})" not in catalog and f"(skills/{s}/)" not in catalog: out.append(f"{s}: not linked in the root README catalog")
    for name in entries:
        if name not in skills: out.append(f"marketplace entry '{name}' has no folder in skills/")
    return out


if __name__ == "__main__":
    p = problems()
    print("\n".join(p) if p else "ok: all skills are consistent")
    sys.exit(1 if p else 0)
