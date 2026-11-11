"""Run reproducible coverage stages and preserve their exact command output."""

import argparse
from datetime import datetime
from html import escape
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
from zoneinfo import ZoneInfo


def run_stage(stage):
    lab = Path(__file__).resolve().parent
    evidence = lab / "evidence"
    evidence.mkdir(exist_ok=True)
    branch = stage == "branch"
    tests = ["BranchCoverageTest_53_bike_share_rental.py" if branch
             else "CodeCoverageTest_53_bike_share_rental.py"]
    env = dict(os.environ, COVERAGE_FILE=str(evidence / f".coverage.{stage}"))
    commands = [
        ["--version"],
        ["-m", "pytest", "--version"],
        ["-m", "coverage", "--version"],
        ["-m", "coverage", "run", "--source=bike_share_rental"]
        + (["--branch"] if branch else [])
        + ["-m", "pytest", "-q"] + tests,
        ["-m", "coverage", "report", "-m", "--fail-under=90"],
        ["-m", "coverage", "json", "-o", f"evidence/{stage}.json"],
        ["-m", "coverage", "html", "-d", f"evidence/html_{stage}"],
    ]
    timestamp = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(timespec="seconds")
    transcript = [f"Lab 6 | {stage.upper()} COVERAGE | {timestamp}",
                  "Working directory: LAB6", ""]
    # Commands use the active interpreter; python below is its display name.
    for args in commands:
        transcript.append("$ python " + shlex.join(args))
        result = subprocess.run([sys.executable, *args], cwd=lab, env=env,
                                text=True, capture_output=True)
        transcript.append(result.stdout.rstrip())
        if result.stderr:
            transcript.append(result.stderr.rstrip())
        transcript.append("")
        if result.returncode:
            raise SystemExit("\n".join(transcript))
    totals = json.loads((evidence / f"{stage}.json").read_text())["totals"]
    transcript.append(
        f"Line coverage: {totals['covered_lines']}/{totals['num_statements']} = "
        f"{100 * totals['covered_lines'] / totals['num_statements']:.2f}%")
    if branch:
        transcript.append(
            f"Branch coverage: {totals['covered_branches']}/{totals['num_branches']} = "
            f"{100 * totals['covered_branches'] / totals['num_branches']:.2f}%")
    text = "\n".join(transcript) + "\n"
    (evidence / f"{stage}_terminal.txt").write_text(text)
    write_transcript_view(evidence, stage, text)
    print(text)


def write_transcript_view(evidence, stage, text):
    # Show the result commands verbatim; the full transcript is kept beside it.
    start = text.index("$ python -m coverage run")
    end = text.index("$ python -m coverage json")
    summary = text[text.index("Line coverage:"):]
    display = text.splitlines()[0] + "\n\n" + text[start:end] + summary
    (evidence / f"{stage}_terminal.html").write_text(
        '<!doctype html><meta charset="utf-8">'
        f'<title>Lab 6 - {stage} coverage command output</title>'
        '<style>body{margin:0;background:#101923;color:#e8eef5;padding:28px;}'
        'h1{font:600 22px system-ui;margin:0 0 8px;color:#8fe4c0;}'
        'p{font:14px system-ui;color:#bac9d8;margin:0 0 22px;}'
        'pre{font:18px/1.55 Menlo,monospace;white-space:pre-wrap;'
        'overflow-wrap:anywhere;margin:0}</style>'
        f'<h1>Lab 6 / {stage.title()} coverage</h1>'
        '<p>Verbatim command output saved by run_coverage.py. '
        'Browser view of the execution transcript.</p>'
        f'<pre>{escape(display)}</pre>'
        f'<p style="margin-top:24px">Full transcript: {stage}_terminal.txt</p>')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["line", "branch"])
    run_stage(parser.parse_args().stage)
