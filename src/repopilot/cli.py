import argparse
import json
from pathlib import Path
from .release_notes import draft_release_notes
from .similarity import find_duplicate_candidates
from .triage import suggest_labels

def main() -> None:
    parser = argparse.ArgumentParser(prog="repopilot")
    commands = parser.add_subparsers(dest="command", required=True)

    labels = commands.add_parser("suggest-labels")
    labels.add_argument("--title", required=True)
    labels.add_argument("--body", default="")

    duplicates = commands.add_parser("duplicates")
    duplicates.add_argument("--input", required=True, type=Path)
    duplicates.add_argument("--threshold", type=float, default=0.35)

    notes = commands.add_parser("release-notes")
    notes.add_argument("--input", required=True, type=Path)
    notes.add_argument("--output", type=Path)

    args = parser.parse_args()
    if args.command == "suggest-labels":
        found = suggest_labels(args.title, args.body)
        print("Suggested labels:", ", ".join(found) if found else "none")
    elif args.command == "duplicates":
        data = json.loads(args.input.read_text(encoding="utf-8"))
        print(json.dumps(find_duplicate_candidates(data, args.threshold), indent=2))
    elif args.command == "release-notes":
        data = json.loads(args.input.read_text(encoding="utf-8"))
        result = draft_release_notes(data)
        if args.output:
            args.output.write_text(result, encoding="utf-8")
            print(f"Release notes written to {args.output}")
        else:
            print(result, end="")
