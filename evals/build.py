#!/usr/bin/env python3
"""Generate `claude plugin eval` cases from the platform-neutral corpus.

The corpus in evals/corpus/*.yaml is the source of truth and is hand-authored.
This script is the Claude Code adapter: it renders each case into the layout
`claude plugin eval` expects. A second adapter will render the same corpus into
Copilot Studio Agent Evaluation test sets, which use a different format and
cannot read these files.

Usage:  python3 evals/build.py [--check]
        --check  exit non-zero if the generated files are out of date
"""
import argparse, json, pathlib, re, shutil, sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent
CORPUS = ROOT / "corpus"
SKILL_NAME = "logistics-billing-reconciliation"

# Read-only tools the skill needs: Read/Glob for its own reference files, Skill to fire.
FRONTMATTER = {
    "max_turns": 20,
    "timeout_seconds": 600,
    "allowed_tools": ["Read", "Glob", "Grep", "Skill"],
}

DOC_TITLES = {
    "freight-invoice": "Freight invoice (the document under audit)",
    "commercial-invoice": "Commercial invoice",
    "packing-list": "Packing list",
    "quote": "Quote",
    "rate-card": "Rate card",
    "surcharge-notice": "Carrier surcharge notice",
}

JS_REGEX_SPECIAL = r"([.*+?^${}()|\[\]\\/])"

# The report template in SKILL.md prints the overall verdict as a symbol under an
# "Overall Verdict" heading. Checking it with a regex is deterministic, free, and it
# doubles as a check that the skill follows its own template. Judge models are left to
# assess the reasoning only -- and never with the words PASS/FAIL used for the subject's
# own verdict, which collides with the judge's own answer vocabulary.
VERDICT_SYMBOL = {
    "PASS": "\u2705",
    "FAIL": "\u274c",
    "REQUIRES CLARIFICATION": "\u2753",
}


def esc(pattern: str) -> str:
    """Escape a literal string for use as a JavaScript regex."""
    return re.sub(JS_REGEX_SPECIAL, r"\\\1", pattern)


def render_prompt(case: dict) -> str:
    fm = dict(FRONTMATTER)
    fm["tags"] = [case.get("class", "unclassified")]
    head = yaml.dump(fm, default_flow_style=None, sort_keys=False).strip()

    if case.get("prompt_override"):
        body = case["prompt_override"].strip()
    else:
        parts = [
            "Can you check this freight invoice for me? I want to know whether we "
            "should pay it as billed. Everything I have is below.",
            "",
        ]
        for key, text in case.get("documents", {}).items():
            parts.append(f"## {DOC_TITLES.get(key, key)}")
            parts.append("")
            parts.append("```")
            parts.append(text.rstrip())
            parts.append("```")
            parts.append("")
        body = "\n".join(parts).rstrip()

    return f"---\n{head}\n---\n\n{body}\n"


def render_graders(case: dict) -> dict:
    exp = case.get("expected", {})
    out = {}

    # One short, single-focus rubric. Long conjunctive rubrics over a long report are
    # what the docs warn against: the judge is small and its votes get noisy.
    out["reasoning.md"] = (
        "---\ntype: llm\nweight: 2\n---\n\n" + exp["criteria"].strip() + "\n"
    )

    symbol = VERDICT_SYMBOL.get(case.get("expected_verdict", ""))
    if symbol:
        out["verdict.md"] = (
            "---\n"
            "type: regex\n"
            f"pattern: 'Overall Verdict[\\s\\S]{{0,60}}{symbol}'\n"
            "weight: 2\n"
            "---\n"
        )

    # Did the skill fire at all? For the non-trigger case, assert it did not.
    if case.get("class") == "non-trigger":
        out["skill-not-fired.md"] = (
            "---\n"
            "type: tool_used\n"
            "tool: Skill\n"
            f"input_match: '\"skill\"\\s*:\\s*\"(?:[\\w-]+:)?{SKILL_NAME}\"'\n"
            "min: 0\n"
            "max: 0\n"
            "---\n"
        )
    else:
        out["skill-fired.md"] = (
            "---\n"
            "type: tool_used\n"
            "tool: Skill\n"
            f"input_match: '\"skill\"\\s*:\\s*\"(?:[\\w-]+:)?{SKILL_NAME}\"'\n"
            "---\n"
        )

    for i, term in enumerate(exp.get("must_mention", []), 1):
        out[f"mentions-{i}.md"] = (
            f"---\ntype: regex\npattern: '{esc(term)}'\n---\n"
        )
    for i, term in enumerate(exp.get("must_not_mention", []), 1):
        out[f"absent-{i}.md"] = (
            f"---\ntype: regex\npattern: '{esc(term)}'\nmatch: not_contains\n---\n"
        )
    return out


def build(check: bool) -> int:
    cases = sorted(CORPUS.glob("*.yaml"))
    if not cases:
        print("no corpus files found", file=sys.stderr)
        return 1

    wanted: dict[pathlib.Path, str] = {}
    for path in cases:
        case = yaml.safe_load(path.read_text(encoding="utf-8"))
        cid = case["id"]
        wanted[ROOT / cid / "prompt.md"] = render_prompt(case)
        for name, text in render_graders(case).items():
            wanted[ROOT / cid / "graders" / name] = text

    if check:
        stale = [
            p for p, text in wanted.items()
            if not p.exists() or p.read_text(encoding="utf-8") != text
        ]
        if stale:
            for p in stale:
                print(f"out of date: {p.relative_to(ROOT.parent)}", file=sys.stderr)
            print("\nrun: python3 evals/build.py", file=sys.stderr)
            return 1
        print(f"{len(cases)} cases up to date")
        return 0

    # Regenerate from scratch so a removed grader does not linger.
    for path in cases:
        cid = yaml.safe_load(path.read_text(encoding="utf-8"))["id"]
        shutil.rmtree(ROOT / cid, ignore_errors=True)
    for p, text in wanted.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    print(f"generated {len(cases)} cases, {len(wanted)} files")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    sys.exit(build(ap.parse_args().check))
