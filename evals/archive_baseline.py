#!/usr/bin/env python3
"""Archive an eval run's scores into evals/baseline/, which is committed.

The no-plugin baseline delta is the one measurement Copilot Studio's Agent Evaluation
has no equivalent for, so it has to be captured here and kept. Run output in
evals/results/ is gitignored and the container is ephemeral; this writes the part
worth keeping.

Usage:  python3 evals/archive_baseline.py [path/to/aggregate-result.json]
        with no argument, uses the most recent run under evals/results/
"""
import json, pathlib, sys, datetime

ROOT = pathlib.Path(__file__).resolve().parent
BASELINE = ROOT / "baseline"


def pick_source(argv) -> pathlib.Path:
    if len(argv) > 1:
        return pathlib.Path(argv[1])
    runs = sorted(ROOT.glob("results/*/aggregate-result.json"))
    if not runs:
        sys.exit("no run found under evals/results/ — run the suite first")
    return runs[-1]


def arm_score(case: dict, arm: str):
    runs = (case.get("arms") or {}).get(arm) or []
    scored = [r["score"] for r in runs if r.get("score") is not None]
    return sum(scored) / len(scored) if scored else None


def main() -> int:
    src = pick_source(sys.argv)
    data = json.loads(src.read_text(encoding="utf-8"))
    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")

    rows = []
    for case in data.get("cases", []):
        with_s = arm_score(case, "with")
        without_s = arm_score(case, "without")
        delta = None if (with_s is None or without_s is None) else with_s - without_s
        rows.append({
            "case": case.get("name"),
            "with": with_s,
            "without": without_s,
            "delta": delta,
            "runs": len((case.get("arms") or {}).get("with") or []),
        })

    deltas = [r["delta"] for r in rows if r["delta"] is not None]
    mean_delta = sum(deltas) / len(deltas) if deltas else None

    BASELINE.mkdir(parents=True, exist_ok=True)
    (BASELINE / f"{stamp}-scores.json").write_text(
        json.dumps({"source": src.name, "rows": rows, "mean_delta": mean_delta},
                   indent=2),
        encoding="utf-8",
    )

    def fmt(v):
        return "  —  " if v is None else f"{v:.2f}"

    lines = [
        f"# Eval baseline — {stamp}",
        "",
        "`WITH` is the case score with the skill loaded, `W/OUT` without it, `Δ` the",
        "difference. A case scoring 1.00 in both arms passes without the skill's help.",
        "",
        "| Case | WITH | W/OUT | Δ |",
        "|------|------|-------|---|",
    ]
    for r in rows:
        d = "  —  " if r["delta"] is None else f"{r['delta']:+.2f}"
        lines.append(f"| {r['case']} | {fmt(r['with'])} | {fmt(r['without'])} | {d} |")
    if mean_delta is not None:
        lines += ["", f"**Mean Δ: {mean_delta:+.2f}** across {len(deltas)} cases."]
    lines += ["", f"Runs per arm: {rows[0]['runs'] if rows else 0}. Source: `{src.name}`."]

    out = BASELINE / f"{stamp}-baseline.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT.parent)}")
    if mean_delta is not None:
        print(f"mean delta {mean_delta:+.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
