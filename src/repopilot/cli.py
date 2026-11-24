import argparse
import json
import os
from pathlib import Path

from .analysis import build_analysis_report
from .dashboard import render_dashboard, serve_dashboard
from .github_client import GitHubAPIError, fetch_open_issues
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

    analyze = commands.add_parser(
        "analyze",
        help="Fetch open issues from a GitHub repository and generate a read-only report.",
    )
    analyze.add_argument("repository", help="GitHub owner/name or repository URL")
    analyze.add_argument("--limit", type=int, default=100, help="Maximum open issues to fetch (1-1000)")
    analyze.add_argument("--threshold", type=float, default=0.35)
    analyze.add_argument("--stale-days", type=int, default=30, help="Days without an update before an issue is stale")
    analyze.add_argument("--output", type=Path, help="Write the JSON report to this path")

    dashboard = commands.add_parser(
        "dashboard",
        help="Create a standalone HTML dashboard or serve an interactive local dashboard.",
    )
    dashboard.add_argument("repository", nargs="?", help="GitHub owner/name or repository URL")
    dashboard.add_argument("--input", type=Path, help="Use an existing JSON analysis report")
    dashboard.add_argument("--limit", type=int, default=100)
    dashboard.add_argument("--threshold", type=float, default=0.35)
    dashboard.add_argument("--stale-days", type=int, default=30)
    dashboard.add_argument("--output", type=Path, help="Write standalone HTML instead of serving")
    dashboard.add_argument("--port", type=int, default=8765)

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
    elif args.command == "analyze":
        try:
            issues = fetch_open_issues(
                args.repository, limit=args.limit, token=os.environ.get("GITHUB_TOKEN")
            )
            report = build_analysis_report(
                args.repository, issues, args.threshold, stale_days=args.stale_days
            )
            rendered = json.dumps(report, indent=2, ensure_ascii=False)
            if args.output:
                args.output.write_text(f"{rendered}\n", encoding="utf-8")
                print(f"Analyzed {len(issues)} open issues from {report['repository']}. Report saved to {args.output}")
            else:
                print(rendered)
        except (GitHubAPIError, ValueError, OSError) as error:
            parser.exit(2, f"{parser.prog}: error: {error}\n")
    elif args.command == "dashboard":
        try:
            if args.input and args.repository:
                parser.error("Use either a repository argument or --input, not both.")
            if not args.input and not args.repository:
                parser.error("Provide a repository or an existing JSON report with --input.")
            if args.input:
                report = json.loads(args.input.read_text(encoding="utf-8"))
            else:
                issues = fetch_open_issues(
                    args.repository, limit=args.limit, token=os.environ.get("GITHUB_TOKEN")
                )
                report = build_analysis_report(
                    args.repository, issues, args.threshold, stale_days=args.stale_days
                )
            document = render_dashboard(report)
            if args.output:
                args.output.write_text(document, encoding="utf-8")
                print(f"HTML dashboard written to {args.output}")
            else:
                serve_dashboard(report, port=args.port)
        except (GitHubAPIError, ValueError, OSError, json.JSONDecodeError) as error:
            parser.exit(2, f"{parser.prog}: error: {error}\n")


if __name__ == "__main__":
    main()
