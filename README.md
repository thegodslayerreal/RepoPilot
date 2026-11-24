# RepoPilot

A local-first toolkit for practical GitHub repository maintenance.

## Features

- Suggest issue labels using transparent keyword rules.
- Find potentially duplicate issues using Jaccard token similarity.
- Draft release notes from merged pull request JSON.
- Fetch open issues from a GitHub repository and analyse them in read-only mode.
- Export repository analysis as JSON.
- Generate a standalone HTML maintainer dashboard or serve an interactive dashboard locally.
- Run a read-only issue suggestion workflow in GitHub Actions.

## Install

Requires Python 3.10+.

~~~bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
~~~

## Try it

~~~bash
repopilot suggest-labels --title "App crashes on startup" --body "It raises an exception"
repopilot duplicates --input examples/issues.json --threshold 0.25
repopilot release-notes --input examples/pulls.json
~~~

## Analyse a live GitHub repository

The analyze command fetches open issues from a public GitHub repository, suggests labels, finds potentially similar issues, and creates a JSON report.

~~~bash
repopilot analyze https://github.com/python/cpython --limit 100 --threshold 0.35 --output report.json
~~~

You can also use the shorter owner/name form:

~~~bash
repopilot analyze pallets/flask --limit 50
~~~

The `--limit` option is a maximum number of issues to analyse, not a guarantee that the repository has that many open issues. GitHub's issues endpoint also returns pull requests, which RepoPilot deliberately excludes. A repository may therefore return fewer issues than the requested limit, including zero.

## Dashboard

Generate a standalone HTML dashboard that can be opened or shared without running a server:

~~~bash
repopilot dashboard pallets/flask --limit 100 --output flask-dashboard.html
~~~

Or start an interactive dashboard on your own computer:

~~~bash
repopilot dashboard pallets/flask --limit 100
~~~

The local dashboard binds to `127.0.0.1` only and opens in your default browser. Stop it with Ctrl+C in the terminal. It includes repository summary metrics, suggested-label distribution, potential duplicate pairs, and a searchable issue table. The standalone HTML export contains the report data and interface in one file and works offline after generation.

You can also create a dashboard from an existing JSON analysis report:

~~~bash
repopilot dashboard --input flask-report.json --output flask-dashboard.html
~~~

## Optional GitHub token

Public repositories can be analysed without authentication. GitHub currently allows 60 unauthenticated REST API requests per hour, per originating IP address. To increase the available rate limit, set a token in your shell before running RepoPilot.

PowerShell:

~~~powershell
$env:GITHUB_TOKEN = "github_pat_your_token"
repopilot analyze owner/repo
~~~

Git Bash:

~~~bash
export GITHUB_TOKEN="github_pat_your_token"
repopilot analyze owner/repo
~~~

Use a token with the minimum permissions required. RepoPilot does not print or store the token. Do not commit tokens to the repository.

## Read-only safety

The live analysis and dashboard commands only fetch repository data. They do not create labels, post comments, assign issues, close issues, or change repository settings. The local dashboard server listens on localhost, not on the public network.

## Development

~~~bash
pip install -e ".[dev]"
pytest
ruff check .
~~~

Tests mock GitHub responses and test dashboard rendering, so the test suite does not require a network connection or a GitHub token.

## Project status

Early development, version 0.1.0. Interfaces may change before 1.0.

## Roadmap

- [x] Rule-based issue label suggestions
- [x] Local duplicate detection baseline
- [x] Release note drafting
- [x] Tests and CI
- [x] Read-only GitHub API integration
- [x] HTML maintainer dashboard and standalone export
- [ ] Repository-specific rule configuration
- [ ] Optional semantic duplicate detection

See CONTRIBUTING.md. Licensed under MIT.
